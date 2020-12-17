# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
import json
import requests


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.sale_id:
            for oline in self.sale_id.order_line:
                if oline.product_id.is_pack and oline.product_id.pack_ids:
                    product = oline.product_id
                    product_tmpl = product.product_tmpl_id
                    sum_prod = sum([ths.product_id.standard_price for ths in product_tmpl.pack_ids])
                    product.sudo().standard_price = sum_prod
        return res

class ProductPack(models.Model):
    _name = 'product.pack'
    _description = 'Product Pack'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, defaults=1.0)
    bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
    bi_image = fields.Binary(related='product_id.image_medium', string='Image', store=True)
    price = fields.Float(related='product_id.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_id.name', readonly="1")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    cal_pack_price = fields.Boolean(string='Calculate Pack Price')
    pack_ids = fields.One2many(comodel_name='product.pack', inverse_name='bi_product_template', string='Product pack')

    @api.model
    def create(self,vals):
        total = 0
        res = super(ProductTemplate,self).create(vals)
        if res.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in res.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            res.list_price = total
        return res

    @api.multi
    def write(self,vals):
        total = 0
        res = super(ProductTemplate, self).write(vals)
        if self.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in self.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            self.list_price = total
        return res

    @api.depends('product_variant_ids', 'product_variant_ids.standard_price', 'pack_ids.product_id.standard_price')
    def _compute_standard_price(self):
        """ Override method _compute_standard_price """
        res = super(ProductTemplate, self)._compute_standard_price()
        for tmpl in self:
            if tmpl.is_pack:
                sum_cost_materials = 0
                for pack in tmpl.pack_ids:
                    sum_cost_materials += pack.product_id.standard_price
                tmpl.standard_price = sum_cost_materials
        return res

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(ProductProduct, self)._convert_prepared_anglosaxon_line(line, partner)
        product = self.search([('id', '=', line.get('product_id', False))])
        if product.is_pack:
            if product.categ_id.property_account_expense_categ_id.id == line['account_id']:
                res['debit'] = line.get('quantity', 0) * product.product_tmpl_id.standard_price
            elif product.categ_id.property_stock_account_input_categ_id.id == line['account_id'] or product.categ_id.property_stock_account_output_categ_id.id == line['account_id']:
                res['credit'] = line.get('quantity', 0) * product.product_tmpl_id.standard_price
        return res
