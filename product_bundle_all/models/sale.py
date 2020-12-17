# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


from odoo import api, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if self.product_id.is_pack:
            warning_mess2 = {}
            if self.product_id.pack_ids:
                if self.product_id.type == 'product':
                    for pack_product in self.product_id.pack_ids:
                        warning_mess = {}
                        qty = self.product_uom_qty
                        if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
                            warning_mess = {
                                    'title': _('Not enough inventory!'),
                                    'message' : ('You plan to sell %s but you only have %s %s available, and the total quantity to sell is %s !' % (qty, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty_uom))
                                    }
                            return {'warning': warning_mess}
            else:
                warning_mess2 = {
                                'title': _('No Product Pack!'),
                                'message' : ('This Product has no product pack materials')
                                }
                return {'warning': warning_mess2}
        else:
            return res

    @api.multi
    def _action_launch_procurement_rule(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                continue
            qty2 = 0.0
            if line.product_id.pack_ids:
                for packs in line.product_id.pack_ids:
                    for moves in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                        if moves.product_id == packs.product_id:
                            qty2 += moves.product_qty

                    if float_compare(qty2, line.product_uom_qty * packs.qty_uom, precision_digits=precision) >= 0:
                        continue
            else:
                qty = line._get_qty_procurement()
                if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                    continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = line.order_id.procurement_group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

#             for line_id in self:
            if line.product_id.pack_ids:
                values = line._prepare_procurement_values(group_id=group_id)
                for val in values:
                    try:
                        pro_id = self.env['product.product'].browse(val.get('product_id'))

                        qty3 = 0.0
                        for moves in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                            if moves.product_id == pro_id:
                                qty3 += moves.product_qty
#                         if float_compare(qty2, val.get('product_qty'), precision_digits=precision) >= 0:
#                             continue

                        product_qty = val.get('product_qty') - qty3

                        # stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
                        product_uom_obj = self.env['product.uom'].browse(val.get('product_uom'))
                        self.env['procurement.group'].run(pro_id, product_qty, product_uom_obj,
                                line.order_id.partner_shipping_id.property_stock_customer,
                                val.get('name'), val.get('origin'), val)
                    except UserError as error:
                        errors.append(error.name)
            else:
                values = line._prepare_procurement_values(group_id=group_id)
                product_qty = line.product_uom_qty - qty
                try:
                    self.env['procurement.group'].\
                        run(line.product_id, product_qty, line.product_uom,
                            line.order_id.partner_shipping_id.property_stock_customer,
                            line.name, line.order_id.name, values)
                except UserError as error:
                    errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _prepare_procurement_values(self, group_id):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        values = []
        date_planned = datetime.strptime(self.order_id.confirmation_date, DEFAULT_SERVER_DATETIME_FORMAT)\
            + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
        if self.product_id.pack_ids:
            for item in self.product_id.pack_ids:
                values.append({
                    'name': item.product_id.name,
                    'origin': self.order_id.name,
                    'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_id': item.product_id.id,
                    'product_qty': item.qty_uom * self.product_uom_qty,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'company_id': self.order_id.company_id.id,
                    'group_id': group_id,
                    'sale_line_id': self.id,
                    'warehouse_id' : self.order_id.warehouse_id and self.order_id.warehouse_id,
                    'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
                    'route_ids': self.route_id and [(4, self.route_id.id)] or [],
                    'partner_dest_id': self.order_id.partner_shipping_id and self.order_id.partner_shipping_id.id,
                })
            return values
        else:
            res.update({
                'company_id': self.order_id.company_id,
                'group_id': group_id,
                'sale_line_id': self.id,
                'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'route_ids': self.route_id,
                'warehouse_id': self.order_id.warehouse_id or False,
                'partner_dest_id': self.order_id.partner_shipping_id
            })    
            return res

    @api.multi
    def _get_delivered_qty(self):
        self.ensure_one()
        order = super(SaleOrderLine, self)._get_delivered_qty()
        picking_ids = self.env['stock.picking'].search([('origin', '=', self.order_id.name)])
        list_of_picking = []
        list_of_pack_product = []
        for pic in picking_ids:
            list_of_picking.append(pic.id)
        if len(picking_ids) >= 1:
            if self.product_id.is_pack:
                for pack_item in self.product_id.pack_ids:
                    list_of_pack_product.append(pack_item.product_id.id)
                stock_move_ids = self.env['stock.move'].\
                    search([('product_id', 'in', list_of_pack_product),
                            ('picking_id', 'in', list_of_picking)])
                pack_delivered = any([move.state == 'done' for move in stock_move_ids])
                if pack_delivered:
                    return self.product_uom_qty
                else:
                    return 0.0
        return order

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'
    
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        
        if  product_id.pack_ids:
            for item in product_id.pack_ids:
                result.update({
                    'product_id': item.product_id.id,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'product_uom_qty': item.qty_uom,
                    'origin': origin,
                    })
        return result

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking=picking)
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_qty
        if  self.product_id.pack_ids:
            for item in self.product_id.pack_ids:
                template = {
                    'name': item.product_id.name or '',
                    'product_id': item.product_id.id,
                    'product_uom': item.uom_id.id,
                    'date': self.order_id.date_order,
                    'date_expected': self.date_planned,
                    'location_id': self.order_id.partner_id.property_stock_supplier.id,
                    'location_dest_id': self.order_id._get_destination_location(),
                    'picking_id': picking.id,
                    'partner_id': self.order_id.dest_address_id.id,
                    'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
                    'state': 'draft',
                    'purchase_line_id': self.id,
                    'company_id': self.order_id.company_id.id,
                    'price_unit': price_unit,
                    'picking_type_id': self.order_id.picking_type_id.id,
                    'group_id': self.order_id.group_id.id,
                    'origin': self.order_id.name,
                    'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
                }
                diff_quantity = item.qty_uom
                if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
                    template['product_uom_qty'] = diff_quantity
                    res.append(template)
            return res
        else:
            template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
            diff_quantity = self.product_qty - qty
            if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                res.append(template)
        return res