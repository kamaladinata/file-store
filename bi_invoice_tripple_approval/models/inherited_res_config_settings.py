# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import fields,models,api, _


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	tripple_invoice_approval = fields.Boolean(string='Tripple Approval ',related="company_id.tripple_invoice_approval")
	third_approval_amount = fields.Float(string="Third Approval Minimum Amount",related="company_id.third_approval_amount")
	

