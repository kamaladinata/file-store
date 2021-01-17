# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductPack(models.Model):
    """ New model Product Pack """
    _name = 'product.pack'
    _description = 'Product Pack'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, default=1.0)
    product_tmpl_id = fields.Many2one('product.template', string='Product Pack')
    image_1920 = fields.Binary(related='product_id.image_1920', string='Image', store=True)
    lst_price = fields.Float(related='product_id.lst_price', string='Product Price', store=True)
    standard_price = fields.Float(related='product_id.standard_price', string='Product Cost', store=True)
    uom_id = fields.Many2one(related='product_id.uom_id' , string='Unit of Measure', readonly='1', store=True)
    name = fields.Char(related='product_id.name', readonly='1')
