# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Company(models.Model):
	_inherit = 'res.company'


	tripple_invoice_approval = fields.Boolean(string='Tripple Approval ')
	third_approval_amount = fields.Float(string="Third Approval Minimum Amount")
	
