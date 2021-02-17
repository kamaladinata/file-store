# -*- coding: utf-8 -*-
from odoo import models,fields,api,exceptions
import datetime

class AgentService(models.Model):
	_name = 'agent.service'
	_inherit = 'frg.service'

	inv_to_consignee_id  = fields.Many2one('bill.instruction')
	due_agent_id         = fields.Many2one('bill.instruction')
	inv_to_agent_id      = fields.Many2one('bill.instruction')
	agent_profit_id      = fields.Many2one('bill.instruction')
	operation_id         = fields.Many2one('frg.operation',string='Operation ',required=False)
	routing_id           = fields.Many2one('frg.carraige',string='Route',required=False)
	vendor_id            = fields.Many2one('res.partner',string='Vendor',required=False)
	qty                  = fields.Integer(string="quantity ")
	line_total           = fields.Float(string="Line Total ")

	payable_ids = fields.Many2many('freight.payable', 'agent_service_freight_payable_rel', 'frg_service_id', 'freight_payable_id', 
		string='Payables'
	)
	receivable_ids = fields.Many2many('freight.receivable', 'agent_service_freight_receivable_rel', 'agent_service_id', 'freight_receivable_id',
		string='Receivables'
	)



class BillInstruction(models.Model):
	_name = 'bill.instruction'
	_rec_name = 'operation_num'

	operation_num        = fields.Many2one("frg.operation",string="Operation No ",required=True)
	date                 = fields.Datetime(string="Date ")
	consignee_id         = fields.Many2one("res.partner",string="Consignee ",required=True)
	agent_id             = fields.Many2one('res.partner', string="Agent ",required=True)
	payment_type         = fields.Selection([('prepaid','Prepaid'),('collect','Collect')],string="Payment Type ")
	PS_for_company       = fields.Integer(string="PS Company(%)",required=True,default=50.0)
	PS_for_agent         = fields.Integer(string="PS Agent(%)",required=True,default=50.0)
	inv_to_consignee_ids = fields.One2many('agent.service',string="Services",inverse_name="inv_to_consignee_id")
	due_agent_ids        = fields.One2many('agent.service',string="Services",inverse_name="due_agent_id")
	inv_to_agent_ids     = fields.One2many('agent.service',string="Services",inverse_name="inv_to_agent_id")
	agent_profit_ids     = fields.One2many('agent.service',string="Services",inverse_name="agent_profit_id")
	invoice_id           = fields.Many2one('account.move',string="Invoice ID")


	#constrains
	@api.constrains('PS_for_company','PS_for_agent')
	def constrains_company_agent_ps(self):
		if (self.PS_for_company < 0) or (self.PS_for_company > 100):
			raise exceptions.ValidationError("the value of PS Company is not valid")
		elif (self.PS_for_agent < 0) or (self.PS_for_agent > 100):
			raise exceptions.ValidationError("the value of PS Agent is not valid")			
	# end constrains	

	@api.onchange('operation_num')
	def onchange_operation(self):
		self.consignee_id = self.operation_num.consignee_id
		self.agent_id     = self.operation_num.agent_id



	@api.onchange('PS_for_company')
	def set_percentage_agent(self):
		self.PS_for_agent = 100 - self.PS_for_company


	@api.onchange('PS_for_agent')
	def set_percentage_company(self):
		self.PS_for_company = 100 - self.PS_for_agent
		
	def update_agent_services(self):
		quantity = 0
		operation_id = self.operation_num
		route_recs        = self.env['frg.carraige'].search([('frg_operation_id', '=', operation_id.id)])
		agent_service_obj = self.env['agent.service']

		# unlink all agent services before update
		for agent_service in agent_service_obj.search([('agent_profit_id','=',self.id)]):
			agent_service.unlink()
		for agent_service in agent_service_obj.search([('inv_to_agent_id','=',self.id)]):
			agent_service.unlink()
		for agent_service in agent_service_obj.search([('due_agent_id','=',self.id)]):
			agent_service.unlink()
		for agent_service in agent_service_obj.search([('inv_to_consignee_id','=',self.id)]):
			agent_service.unlink()													


		for route in route_recs:
			if route.rtype == 'main':
				for package in route.route_order_line_ids:
					quantity += package.pieces	

				for service in route.service_ids:
					if not service.lump_sum and service.main:
						inv_to_consignee_ids_vals = {
							'qty':quantity,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.sale,
							'curr_id': service.curr_id.id,
							'inv_to_consignee_id':self.id,
							'line_total':(quantity*service.sale)
						}

						due_agent_ids_vals = {
							'qty':quantity,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.cost,
							'curr_id': service.curr_id.id,
							'due_agent_id':self.id,
							'line_total':(quantity*service.cost)
						}

						due_agent_ids_profit_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'Total profit',
							'sale': (service.sale*quantity)-(service.cost*quantity),
							'curr_id': service.curr_id.id,
							'due_agent_id':self.id,
							'line_total':(service.sale*quantity)-(service.cost*quantity)
						}


						inv_to_agent_ids_vals = {
							'qty':quantity,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.cost,
							'curr_id': service.curr_id.id,
							'inv_to_agent_id':self.id,
							'line_total':(quantity*service.cost)
						}

						inv_to_agent_ids_profit_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'My Company Profit',
							'sale': ((service.sale*quantity)-(service.cost*quantity))*self.PS_for_company/100,
							'curr_id': service.curr_id.id,
							'inv_to_agent_id':self.id,
							'line_total':((service.sale*quantity)-(service.cost*quantity))*self.PS_for_company/100
						}

						agent_profit_ids_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'Agent Profit',
							'sale': ((service.sale*quantity)-(service.cost*quantity))*self.PS_for_agent/100,
							'curr_id': service.curr_id.id,
							'agent_profit_id':self.id,
							'line_total':((service.sale*quantity)-(service.cost*quantity))*self.PS_for_agent/100
						}												

						created = agent_service_obj.create(inv_to_consignee_ids_vals)
						created = agent_service_obj.create(due_agent_ids_vals)
						created = agent_service_obj.create(due_agent_ids_profit_vals)
						created = agent_service_obj.create(inv_to_agent_ids_vals)
						created = agent_service_obj.create(inv_to_agent_ids_profit_vals)
						created = agent_service_obj.create(agent_profit_ids_vals)

					elif service.lump_sum and service.main:
						inv_to_consignee_ids_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.sale,
							'curr_id': service.curr_id.id,
							'inv_to_consignee_id':self.id,
							'line_total':(service.sale)
						}
						due_agent_ids_profit_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'Total profit',
							'sale': (service.sale - service.cost),
							'curr_id': service.curr_id.id,
							'due_agent_id':self.id,
							'line_total':(service.sale - service.cost)
						}
						due_agent_ids_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.cost,
							'curr_id': service.curr_id.id,
							'due_agent_id':self.id,
							'line_total':(service.cost)
						}

						inv_to_agent_ids_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'On Site Monitoring Port Of ' + route.dis_port_id.name,
							'sale': service.cost,
							'curr_id': service.curr_id.id,
							'inv_to_agent_id':self.id,
							'line_total':(service.cost)
						}

						inv_to_agent_ids_profit_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'My Company Profit',
							'sale': (service.sale - service.cost)*self.PS_for_company/100,
							'curr_id': service.curr_id.id,
							'inv_to_agent_id':self.id,
							'line_total':(service.sale - service.cost)*self.PS_for_company/100
						}

						agent_profit_ids_vals = {
							'qty':1,
							'product_id':service.product_id.id,
							'name': 'Agent Profit',
							'sale': (service.sale - service.cost)*self.PS_for_agent/100,
							'curr_id': service.curr_id.id,
							'agent_profit_id':self.id,
							'line_total':(service.sale - service.cost)*self.PS_for_agent/100
						}						

						created = agent_service_obj.create(inv_to_consignee_ids_vals)
						created = agent_service_obj.create(due_agent_ids_vals)
						created = agent_service_obj.create(due_agent_ids_profit_vals)
						created = agent_service_obj.create(inv_to_agent_ids_vals)
						created = agent_service_obj.create(inv_to_agent_ids_profit_vals)							
						created = agent_service_obj.create(agent_profit_ids_vals)
						
	def create_invoice(self):
		if not self.invoice_id:
			quantity = 0
			agent_service_obj = self.env['agent.service']
			route_recs        = self.env['frg.carraige'].search([])
			route_currency_id = False
			for route in route_recs:
				if route.rtype == 'main':
					for package in route.route_order_line_ids:
						quantity += package.pieces	

			for service in route.service_ids:
				route_currency_id = service.curr_id.id
				if not service.lump_sum and service.main:
					company_profit_vals = {
						'product_id':service.product_id.id,
						'name':'My Company Profit',
						'quantity':quantity,
						'move_id':self.id,
						'account_id':self.agent_id.property_account_payable_id.id,					
						'price_unit':((service.sale*quantity)-(service.cost*quantity))*self.PS_for_company/100,
						'price_subtotal':((service.sale*quantity)-(service.cost*quantity))*self.PS_for_company/100
					}
					service_cost_vals = {
						'product_id':service.product_id.id,
						'name':'Service Cost',
						'quantity':1,
						'move_id':self.id,
						'account_id':self.agent_id.property_account_payable_id.id,					
						'price_unit':(service.cost*quantity),
						'price_subtotal':(service.cost*quantity)
					}

					company_profit_rec = self.env['account.move.line'].create(company_profit_vals)
					service_cost_rec   = self.env['account.move.line'].create(service_cost_vals)
				
				elif service.lump_sum and service.main:
					company_profit_vals = {
						'product_id':service.product_id.id,
						'name':'My Company Profit',
						'quantity':1,
						'move_id':self.id,
						'account_id':self.agent_id.property_account_payable_id.id,					
						'price_unit':(service.sale-service.cost)*self.PS_for_company/100,
						'price_subtotal':(service.sale-service.cost)*self.PS_for_company/100
					}

					service_cost_vals = {
						'product_id':service.product_id.id,
						'name':'Service Cost',
						'quantity':1,
						'move_id':self.id,
						'account_id':self.agent_id.property_account_payable_id.id,					
						'price_unit':(service.cost),
						'price_subtotal':(service.cost)
					}
					company_profit_rec = self.env['account.move.line'].create(company_profit_vals)
					service_cost_rec   = self.env['account.move.line'].create(service_cost_vals)
				invoice_vals = {
				  'type':'out_invoice',
				  'invoice_date':fields.date.today().strftime('%Y-%m-%d'),
				  'account_id':self.agent_id.property_account_payable_id.id,
				  'partner_id': self.agent_id.id,
				  'currency_id':route_currency_id
				}
				invoice = self.env['account.move'].create(invoice_vals)
				company_profit_rec.invoice_id = invoice
				service_cost_rec.invoice_id   = invoice
				self.invoice_id = invoice

	def view_invoice(self):
		self.ensure_one()
		if self.invoice_id:
			service_to_invoice_action = {
				'view_mode':'tree,form',
				'view_type':'form',
				'res_model':'account.move',
				'type':'ir.actions.act_window',
				'target':'current',
				'domain':[('id','=',self.invoice_id.id)]
			}

			return service_to_invoice_action										
