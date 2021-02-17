from odoo import models, fields, api, tools, _
from odoo import exceptions
import datetime
import itertools 

class FreightPayable(models.Model):
	_name='freight.payable'
	_inherits = {'account.move.line': 'invoice_line_id'}
	_description = 'Payable '

	invoice_line_id = fields.Many2one('account.move.line',string='Invoice Line',ondelete='restrict', required=True, auto_join=True)
	vendor_id=fields.Many2one('res.partner',string="Vendor ",required=True)
	curr_id=fields.Many2one('res.currency',string="Currency: ",required=True)
	invoice_state = fields.Selection(string='Invoice state',store=True,related='move_id.state')
	payable_wizard_ids=fields.Many2many('freight.payable.wizard',relation='payable_invoice_id')
	payable_batch_invoices_wizard_ids=fields.Many2many('freight.payable.batch.invoices.wizard',relation="rel_payable_batch_wizard")
	operation_payable_id = fields.Many2one('frg.operation',string="Operation",required=True)
	payable_amount = fields.Float(compute="_get_payables_amount")

	payable_service_ids = fields.Many2many('frg.service', 'freight_payable_frg_service_rel', 'freight_payable_id', 'frg_service_id',
		string='Payable Services'
	)

	uom = fields.Selection(
		string='UOM',
		required=True,
		default='fix',
		help= "The 'Unit of Measure' used for Recievalbe and Payables caluclation of this service"\
			  "Fixed is used to calculate payable/receivable  total pieces based on qty of the pacakges"\
			  "Gross weight calculate qty based on Total Gross weight of the pacakges"\
			  "Chargeable weight calculate qty based on Total Chargeable weight of the pacakges",
		selection=[('fix', 'Fixed'), ('gw', 'Gross Weight'),('cw', 'Chargeable Weight')]
	)

	@api.depends('price_unit','curr_id','quantity')
	def _get_payables_amount(self):
		main_currency = self.env.user.company_id.currency_id
		amount = self.curr_id.compute(self.price_unit,main_currency)
		self.payable_amount = amount*self.quantity


	@api.onchange('product_id')
	def set_account_id(self):
		if self.product_id:
			self.account_id = self.product_id.property_account_expense_id.id


class PayableWizard(models.TransientModel):
	_name='freight.payable.wizard'


	def _default_payables(self):
		payables = self.env['freight.payable'].browse(self._context.get('active_ids'))
		payables_without_invoice = payables.filtered(lambda r: r.move_id.id == False)
		return payables_without_invoice

	def _default_vendor(self):
		payables = self.env['freight.payable'].browse(self._context.get('active_ids'))
		payables_without_invoice = payables.filtered(lambda r: r.move_id.id == False)
		all_vendors = []
		for payable in payables_without_invoice:
			if not payable.move_id and (payable.vendor_id not in all_vendors):
				all_vendors.append(payable.vendor_id)
		if len(all_vendors) == 1:
			return payable.vendor_id
							

	def _default_currency(self):
		payables = self.env['freight.payable'].browse(self._context.get('active_ids'))
		payables_without_invoice = payables.filtered(lambda r: r.move_id.id == False)
		all_currencies = []
		for payable in payables_without_invoice:
			if not payable.invoice_id and (payable.curr_id not in all_currencies):
				all_currencies.append(payable.curr_id)
		if len(all_currencies) == 1:	
			return payable.curr_id				

	vendor_id = fields.Many2one('res.partner',string='Vendor ',required=True,default=_default_vendor)
	curr_id=fields.Many2one('res.currency',string="Currency ",required=True,default=_default_currency)
	invoice_line_ids= fields.Many2many('freight.payable',string="Payable Invoice lines",default=_default_payables,relation='payable_invoice_id')

	def create_invoice(self):
		self.ensure_one()
		payable_ids = []
		if self.invoice_line_ids:
			for line in self.invoice_line_ids:
				if(line.curr_id != self.curr_id):
					raise exceptions.ValidationError('Invalid currency '+str(line.curr_id.name))

				if(line.vendor_id != self.vendor_id):
					raise exceptions.ValidationError('Invalid Vendor '+str(line.vendor_id.name))
			# Create a new invoice with these values
			invoice = self.env['account.move'].create({'type': 'in_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': self.vendor_id.property_account_payable_id.id,'partner_id': self.vendor_id.id,'currency_id': self.curr_id.id})
			invoice_id = invoice.id
			vals = []
			for line in self.invoice_line_ids:
				line.invoice_id = invoice
				payable_ids.append(invoice.id)

			payable_action = {
				'name': 'Invoices',
				'view_mode':'tree,form',
				'view_type':'form',
				'res_model':'account.move',
				'type':'ir.actions.act_window',
				'target':'current',
				'domain':[('id','in',payable_ids)]
			}				 
			return payable_action


			
class payable_batch_invoices_wizard(models.TransientModel):
	_name = 'freight.payable.batch.invoices.wizard'

	def _default_payables(self):
		payables = self.env['freight.payable'].browse(self._context.get('active_ids'))
		payables_without_invoice = payables.filtered(lambda r: r.move_id.id == False)
		return payables_without_invoice

	def _default_number_of_invoices(self):
		payables = self.env['freight.payable'].browse(self._context.get('active_ids'))
		payables_without_invoice = payables.filtered(lambda r: r.move_id.id == False)
		unique_vendors = []
		number_of_invoices = 0
		for payable in payables_without_invoice:
			if payable.vendor_id not in unique_vendors:
				unique_vendors.append(payable.vendor_id)
		number_of_invoices += len(unique_vendors)
		return number_of_invoices		

	invoice_line_ids= fields.Many2many('freight.payable',string="Payable Invoice lines",default=_default_payables,relation="rel_payable_batch_wizard")
	number_of_invoices = fields.Integer(string="Number Of Invoices",default=_default_number_of_invoices)
	invoice_batch_type = fields.Selection([('per_line','Per Line'),('all_lines','All Lines')],default='all_lines')

	def create_batch_invoices(self):
		self.ensure_one()
		if self.invoice_line_ids:
			payable_ids = []
			if self.invoice_batch_type == 'per_line':
				for line in self.invoice_line_ids:
					invoice = self.env['account.move'].create({'type': 'in_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': line.vendor_id.property_account_payable_id.id,'partner_id': line.vendor_id.id ,'currency_id': line.curr_id.id})
					line.move_id=invoice
					payable_ids.append(invoice.id) 
					
				payable_action = {
					'name': 'Invoices',				
					'view_mode':'tree,form',
					'view_type':'form',
					'res_model':'account.move',
					'type':'ir.actions.act_window',
					'target':'current',
					'domain':[('id','in',payable_ids)]
				}

				return payable_action			
			else:	
				payables = ()
				invoices = []
				vendorCurrency = ''
				for line in self.invoice_line_ids:
					vendorCurrency = str(line.curr_id.id) +','+ str(line.vendor_id.id)
					payables = (line.id,vendorCurrency)
					invoices.append(payables)	


				for key, group in itertools.groupby(invoices, lambda x:x[1]):
					c_id,v_id = key.split(',')
					vendor_id = int(v_id)
					vendor_rec = self.env['res.partner'].browse(vendor_id)
					invoice = self.env['account.move'].create({'type': 'in_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': vendor_rec.property_account_payable_id.id,'partner_id': int(v_id),'currency_id': int(c_id)})
					payable_ids.append(invoice.id)

					for g in group:
						invoice_line_id = g[0]
						inv_line = self.env['freight.payable'].browse(invoice_line_id)
						inv_line.move_id = invoice


				payable_action = {
					'name': 'Invoices',
					'view_mode':'tree,form',
					'view_type':'form',
					'res_model':'account.move',
					'type':'ir.actions.act_window',
					'target':'current',
					'domain':[('id','in',payable_ids)]
				}

				return payable_action