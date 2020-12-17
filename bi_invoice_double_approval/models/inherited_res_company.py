# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Company(models.Model):
	_inherit = 'res.company'


	double_invoice_approval = fields.Boolean(string='Double Approval :')
	first_approval_amount = fields.Float(string="First Approval Minimum Amount")
	second_approval_amount = fields.Float(string="First Approval Minimum Amount")
