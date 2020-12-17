# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    down_payment_product_id = fields.Many2one('product.product', string='Down Payment Product')



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    down_payment_product_id = fields.Many2one('product.product',
                                              related='company_id.down_payment_product_id',
                                              string='Down Payment Product',
                                              readonly=False)
