# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class AccountAsset(models.Model):

    _inherit='account.asset'

    asset_tag_number = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Vendor')
    location = fields.Char()
