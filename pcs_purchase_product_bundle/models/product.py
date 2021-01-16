# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
import json
import requests


class ProductTemplate(models.Model):
    """Inherit Product Template"""
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    is_calpack_price = fields.Boolean(string='Calculate Pack Price')
    product_pack_ids = fields.One2many('product.pack', 'product_tmpl_id', string='Product Packs')

    @api.model
    def create(self,vals):
        total = 0
        res = super(ProductTemplate,self).create(vals)
        if res.is_calpack_price:
            if 'product_pack_ids' in vals or 'is_calpack_price' in vals:
                    for pack_product in res.product_pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            res.list_price = total
        return res

    def write(self,vals):
        total = 0
        res = super(ProductTemplate, self).write(vals)
        if self.is_calpack_price:
            if 'product_pack_ids' in vals or 'is_calpack_price' in vals:
                    for pack_product in self.product_pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            self.list_price = total
        return res

    @api.depends_context('company')
    @api.depends('product_variant_ids', 'product_variant_ids.standard_price', 'product_pack_ids.product_id.standard_price')
    def _compute_standard_price(self):
        """ Override method _compute_standard_price """
        res = super(ProductTemplate, self)._compute_standard_price()
        for tmpl in self:
            if tmpl.is_pack:
                sum_cost_materials = 0
                for pack in tmpl.product_pack_ids:
                    sum_cost_materials += pack.product_id.standard_price
                tmpl.standard_price = sum_cost_materials
        return res
