from odoo import models, fields, api, tools, _
from odoo import exceptions
import datetime
import itertools  

class FreightReceivable(models.Model):
	_name='freight.receivable'
	_inherits = {'account.move.line': 'invoice_line_id'}
	_description = 'Receivable '
	
	invoice_line_id = fields.Many2one('account.move.line',string='Invoice Line: ',ondelete='restrict', required=True, auto_join=True)
	receivable_wizard_ids=fields.Many2many('freight.receivable.wizard',relation='receivable_invoice_id')
	receivable_batch_invoices_wizard_ids=fields.Many2many('freight.receivable.batch.invoices.wizard',relation="rel_receivable_batch_wizard")
	curr_id=fields.Many2one('res.currency',string="Currency: ",required=True)
	invoice_state = fields.Selection(string='Invoice state',store=True,related='move_id.state')
	operation_receivable_id = fields.Many2one('frg.operation',string="Operation",required=True)	
	receivable_amount = fields.Float(compute="_get_receivables_amount")

	receive_service_ids = fields.Many2many('frg.service', 'freight_receivable_frg_service_rel', 'freight_receivable_id', 'frg_service_id',
		string='Receivable Services'
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


	@api.onchange('uom')
	def change_uom(self):
		pass

	@api.depends('quantity','curr_id','price_unit')
	def _get_receivables_amount(self):
		for obj in self:
			main_currency = self.env.user.company_id.currency_id
			amount = obj.curr_id.compute(obj.price_unit,main_currency)
			obj.receivable_amount = amount*obj.quantity



	@api.onchange('product_id')
	def set_account_id(self):
		self.account_id = self.product_id.property_account_income_id.id



class ReceivableWizard(models.TransientModel):
	_name='freight.receivable.wizard'


	def _default_receivables(self):
		receivables =  self.env['freight.receivable'].browse(self._context.get('active_ids'))
		receivables_without_invoice = receivables.filtered(lambda r: r.move_id.id == False)
		return receivables_without_invoice


	def _default_operation(self):
		return self.env['freight.receivable'].browse(self._context.get('active_ids'))[0].operation_receivable_id
	

	def _default_currency(self):
		receivables = self.env['freight.receivable'].browse(self._context.get('active_ids'))
		receivables_without_invoice = receivables.filtered(lambda r: r.move_id.id == False)
		all_currencies = []
		for receivable in receivables_without_invoice:
			if receivable.curr_id not in all_currencies:
				all_currencies.append(receivable.curr_id)
		if len(all_currencies) == 1:	
			return receivable.curr_id			


	customer_id = fields.Many2one('res.partner',string='Customer : ',required=True,store=True,compute='_get_customer',inverse='_set_customer')
	curr_id=fields.Many2one('res.currency',string="Currency: ",required=True,default=_default_currency)
	operation_id=fields.Many2one('frg.operation',default=_default_operation)
	invoice_line_ids= fields.Many2many('freight.receivable',string="Receivable Invoice lines",default=_default_receivables,relation='receivable_invoice_id')
	customer_type = fields.Selection(string='Customer type',selection=[('shipper', 'Shipper'), ('consignee', 'Consignee'),('agent','Agent'),('customer_operation','Customer Operation')])
	
	@api.depends('customer_type')
	def _get_customer(self):
		self.ensure_one()
		if(self.customer_type=='shipper'):
			self.customer_id = self.operation_id.shipper_id

		elif(self.customer_type=='consignee'):
			self.customer_id = self.operation_id.consignee_id

		elif(self.customer_type=='agent'):
			self.customer_id = self.operation_id.agent_id

	def _set_customer(self):
		pass

	def create_invoice(self):
		self.ensure_one()
		receivable_ids = []
		if self.invoice_line_ids:
			for line in self.invoice_line_ids:
				if(line.curr_id != self.curr_id):
					raise exceptions.ValidationError('Invalid currency '+str(line.curr_id.name))

			# Create a new invoice with these values
			invoice=self.env['account.move'].create({'type': 'out_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': self.customer_id.property_account_receivable_id.id,'partner_id': self.customer_id.id,'currency_id': self.curr_id.id})
			invoice_id=invoice.id
			# Take the invoice_id and add it to all invoice_lines
			for line in self.invoice_line_ids:
				if not line.move_id:
					line.move_id = invoice
					receivable_ids.append(invoice.id)

			receivable_action = {
				'name': 'Invoices',
				'view_mode':'tree,form',
				'view_type':'form',
				'res_model':'account.move',
				'type':'ir.actions.act_window',
				'target':'current',
				'domain':[('id','in',receivable_ids)]
			}

			return receivable_action




class receivable_batch_invoices_wizard(models.TransientModel):
	_name = 'freight.receivable.batch.invoices.wizard'

	def _default_operation(self):
		return self.env['freight.receivable'].browse(self._context.get('active_ids'))[0].operation_receivable_id

	def _default_receivables(self):
		receivables = self.env['freight.receivable'].browse(self._context.get('active_ids'))
		receivables_without_invoice = receivables.filtered(lambda r: r.invoice_id.id == False)
		return receivables_without_invoice

	def _default_number_of_invoices(self):
		receivables = self.env['freight.receivable'].browse(self._context.get('active_ids'))
		receivables_without_invoice = receivables.filtered(lambda r: r.invoice_id.id == False)
		number_of_invoices = 0
		for receivable in receivables_without_invoice:
			number_of_invoices += len(receivable.curr_id)
		return number_of_invoices		

	customer_id = fields.Many2one('res.partner',string='Customer : ',required=True,store=True,compute='_get_customer',inverse='_set_customer')
	customer_type = fields.Selection(string='Customer type',selection=[('shipper', 'Shipper'), ('consignee', 'Consignee'),('agent','Agent'),('customer_operation','Customer Operation')])
	invoice_line_ids= fields.Many2many('freight.receivable',string="Receivable Invoice lines",default=_default_receivables,relation="rel_receivable_batch_wizard")
	number_of_invoices = fields.Integer(string="Number Of Invoices",default=_default_number_of_invoices)
	operation_id = fields.Many2one('frg.operation',default=_default_operation)
	invoice_batch_type = fields.Selection([('per_line','Per Line'),('all_lines','All Lines')],default='all_lines')

	@api.depends('customer_type')
	def _get_customer(self):
		self.ensure_one()
		if(self.customer_type=='shipper'):
			self.customer_id = self.operation_id.shipper_id

		elif(self.customer_type=='consignee'):
			self.customer_id = self.operation_id.consignee_id

		elif(self.customer_type=='agent'):
			self.customer_id = self.operation_id.agent_id

	def _set_customer(self):
		pass

	def create_batch_invoices(self):
		self.ensure_one()
		if self.invoice_line_ids:
			receivable_ids = []
			if self.invoice_batch_type == 'per_line':
				for line in self.invoice_line_ids:
					invoice = self.env['account.move'].create({'type': 'out_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': self.customer_id.property_account_payable_id.id,'partner_id': self.customer_id.id ,'currency_id': line.curr_id.id})
					line.invoice_id = invoice
					receivable_ids.append(invoice.id)

				receivable_action = {
					'name': 'Invoices',
					'view_mode':'tree,form',
					'view_type':'form',
					'res_model':'account.move',
					'type':'ir.actions.act_window',
					'target':'current',
					'domain':[('id','in',receivable_ids)]
				}

				return receivable_action

			else:			
				receivables = ()
				invoices = []
				currency = ''
				for line in self.invoice_line_ids:
					currency = str(line.curr_id.id)
					receivables = (line.id,currency)
					invoices.append(receivables)	


				for key, group in itertools.groupby(invoices, lambda x:x[1]):
					currency = key
					invoice = self.env['account.move'].create({'type': 'out_invoice','invoice_date': fields.date.today().strftime('%Y-%m-%d'),'account_id': self.customer_id.property_account_receivable_id.id,'partner_id': self.customer_id.id,'currency_id': currency})
					receivable_ids.append(invoice.id)

					for g in group:
						invoice_line_id = g[0]
						inv_line = self.env['freight.receivable'].browse(invoice_line_id)
						if not inv_line.invoice_id:
							inv_line.invoice_id = invoice

				receivable_action = {
					'name': 'Invoices',
					'view_mode':'tree,form',
					'view_type':'form',
					'res_model':'account.move',
					'type':'ir.actions.act_window',
					'target':'current',
					'domain':[('id','in',receivable_ids)]
				}

				return receivable_action										