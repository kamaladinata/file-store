# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import fields,models,api, _


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	double_invoice_approval = fields.Boolean(string='Double Approval ',related="company_id.double_invoice_approval")
	first_approval_amount = fields.Float(string="First Approval Minimum Amount",related="company_id.first_approval_amount")
	second_approval_amount = fields.Float(string="Second Approval Minimum Amount",related="company_id.second_approval_amount")

