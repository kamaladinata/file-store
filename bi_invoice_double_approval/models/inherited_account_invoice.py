# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import fields,models,api, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	state = fields.Selection([
			('draft','Draft'),
			('approve','To Approve'),
			('second_approve','Second Approve'),
			('open', 'Open'),
			('paid', 'Paid'),
			('cancel', 'Cancelled'),
		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False,
		help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
			 " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
			 " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
			 " * The 'Cancelled' status is used when user cancel invoice.")

	@api.multi
	def action_invoice_open(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		res = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
		
		if res.double_invoice_approval == True and res.first_approval_amount < self.amount_total :
			
			for order in self :
				order.write({'state':'approve'})

			return True


		else :
			to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
			if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
				raise UserError(_("Invoice must be in draft state in order to validate it."))
			if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
				raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
			to_open_invoices.action_date_assign()
			to_open_invoices.action_move_create()
			return to_open_invoices.invoice_validate()

	@api.multi
	def action_approve(self):
		res = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)

		if res.double_invoice_approval == True and res.second_approval_amount < self.amount_total :
			
			for order in self :
				order.write({'state':'second_approve'})

			return True


		else :
			to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
			if to_open_invoices.filtered(lambda inv: inv.state != 'approve'):
				raise UserError(_("Invoice must be in draft state in order to validate it."))
			if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
				raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
			to_open_invoices.action_date_assign()
			to_open_invoices.action_move_create()
			return to_open_invoices.invoice_validate()


	@api.multi
	def action_second_approve(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')

		if to_open_invoices.filtered(lambda inv: inv.state != 'second_approve'):
			raise UserError(_("Invoice must be in Second Approve state in order to validate it."))
		if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
			raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
		to_open_invoices.action_date_assign()
		to_open_invoices.action_move_create()
		return to_open_invoices.invoice_validate()