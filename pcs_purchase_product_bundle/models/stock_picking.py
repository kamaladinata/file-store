# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    """Inherit Stock Picking"""
    _inherit = "stock.picking"

    def action_done(self):
        """ Inherit this function to update product cost when the product is product bundle"""
        res = super(StockPicking, self).action_done()
        if self.purchase_id:
            for oline in self.purchase_id.order_line.filtered(lambda l: l.product_id.is_pack and l.product_id.product_pack_ids):
                product_tmpl_id = oline.product_id.product_tmpl_id
                sum_prod = sum([pack.product_id.standard_price * pack.qty_uom for pack in product_tmpl_id.product_pack_ids])
                oline.product_id.sudo().standard_price = sum_prod
        return res
