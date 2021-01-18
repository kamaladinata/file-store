# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    """Inherit Product Template"""
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    is_calpack_price = fields.Boolean(string='Calculate Pack Price')
    product_pack_ids = fields.One2many('product.pack', 'product_tmpl_id', string='Product Packs')

    @api.model_create_multi
    def create(self, vals):
        """ Inherit function create product to canculate product price and cost
            - the calculation will be run when the user create a product with is_calpack_price field is ticked
        """
        total_price = total_cost = 0
        res = super(ProductTemplate,self).create(vals)
        if res.is_calpack_price:
            if 'product_pack_ids' in vals or 'is_calpack_price' in vals:
                for pack_product in res.product_pack_ids:
                    total_price += pack_product.product_id.list_price * pack_product.qty_uom
                    total_cost += pack_product.product_id.standard_price * pack_product.qty_uom 
        if total_price > 0:
            res.list_price = total_price
        if total_cost > 0:
            res.standard_price = total_cost
        return res

    def write(self, vals):
        """ Inherit function write product to canculate product price and cost
            - the calculation will be run when the user create a product with is_calpack_price field is ticked
        """
        total_price = total_cost = 0
        res = super(ProductTemplate, self).write(vals)
        if self.is_calpack_price:
            if 'product_pack_ids' in vals or 'is_calpack_price' in vals:
                for pack_product in self.product_pack_ids:
                    total_price += pack_product.product_id.list_price * pack_product.qty_uom 
                    total_cost += pack_product.product_id.standard_price * pack_product.qty_uom 
        if total_price > 0:
            self.list_price = total_price
        if total_cost > 0:
            self.standard_price = total_cost
        return res

    @api.depends_context('company')
    @api.depends('product_variant_ids', 'product_variant_ids.standard_price', 'product_pack_ids.standard_price')
    def _compute_standard_price(self):
        """ Inherit method _compute_standard_price to canculate product cost, depends on product_pack_ids.standard_price """
        res = super(ProductTemplate, self)._compute_standard_price()
        for tmpl in self:
            if tmpl.is_pack:
                sum_cost_materials = 0
                for pack in tmpl.product_pack_ids:
                    sum_cost_materials += pack.product_id.standard_price * pack.qty_uom
                tmpl.standard_price = sum_cost_materials
        return res
