# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    """Inherit Stock Picking"""
    _inherit = "stock.picking"

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.purchase_id:
            for oline in self.purchase_id.order_line:
                if oline.product_id.is_pack and oline.product_id.product_pack_ids:
                    product = oline.product_id
                    product_tmpl = product.product_tmpl_id
                    sum_prod = sum([ths.product_id.standard_price for ths in product_tmpl.product_pack_ids])
                    product.sudo().standard_price = sum_prod
        return res
