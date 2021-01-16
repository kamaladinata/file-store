# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    """Inherit Purchase Order Line"""
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
            line.move_dest_ids.created_purchase_line_id = False
        
        new_values = []
        for val in values:
            product_id = val.get('product_id')
            product_id = self.env['product.product'].browse(product_id)
            if product_id.is_pack and product_id.product_pack_ids:
                picking_type = self.env['stock.picking.type'].browse(val.get('picking_type_id'))
                for pack in product_id.product_pack_ids:
                    line_uom = self.env['uom.uom'].browse(val.get('product_uom'))
                    quant_uom = pack.uom_id
                    product_qty = pack.qty_uom * val.get('product_uom_qty')
                    product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                    vals = {
                        'name': pack.product_id.name, 
                        'product_id': pack.product_id.id, 
                        'date': val.get('date'), 
                        'date_deadline': val.get('date_deadline'), 
                        'location_id': val.get('location_id'), 
                        'location_dest_id': val.get('location_dest_id'), 
                        'picking_id': val.get('picking_id'), 
                        'partner_id': val.get('partner_id'), 
                        'move_dest_ids': val.get('move_dest_ids'), 
                        'state': val.get('state'),  
                        'purchase_line_id': val.get('purchase_line_id'), 
                        'company_id': val.get('company_id'), 
                        'price_unit': pack.lst_price, 
                        'picking_type_id': val.get('picking_type_id'), 
                        'group_id': val.get('group_id'), 
                        'origin': val.get('origin'), 
                        'description_picking': product_id._get_description(picking_type), 
                        'propagate_cancel': val.get('propagate_cancel'), 
                        'route_ids': val.get('route_ids'),
                        'warehouse_id': val.get('warehouse_id'),
                        'product_uom_qty': product_qty,
                        'product_uom': procurement_uom.id,
                    }
                    new_values.append(vals)
            else:
                new_values.append(val)

        return self.env['stock.move'].create(new_values)
    
    @api.depends('move_ids.state', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_received(self):
        res = super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self:
            picking_ids = self.env['stock.picking'].search([('origin', '=', line.order_id.name)])
            list_of_picking = []
            for pic in picking_ids:
                list_of_picking.append(pic.id)
            if list_of_picking:
                if line.product_id.is_pack and line.product_id.product_pack_ids:
                    list_of_pack_product = []
                    for pack_item in line.product_id.product_pack_ids:
                        list_of_pack_product.append(pack_item.product_id.id)
                    stock_move_ids = self.env['stock.move'].search([('product_id', 'in', list_of_pack_product), ('picking_id', 'in', list_of_picking)])
                    pack_received = any([move.state == 'done' for move in stock_move_ids])
                    if pack_received:
                        qty_done = sum(stock_move_ids.filtered(lambda sm: sm.state == 'done').mapped('quantity_done'))
                        line.qty_received += qty_done
                    else:
                        line.qty_received = 0.0
        return res