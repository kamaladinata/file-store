from odoo import models, fields, api, tools,exceptions, _
from datetime import date
from datetime import time
from datetime import datetime

from odoo.addons.freight_management.models.operations import FrgOperation

VTW_CONV_INLAND = 333.00
VTW_CONV_OCEAN = 1000.00
VTW_CONV_AIR = 167.00


class operation(models.Model):
    _inherit = 'frg.operation'

    def _get_loading_port_label(self):
        for obj in self:
            val = "gateway"
            if obj.transport and obj.transport != 'air':
                val = "loading_port"
            obj.load_port_lable = val

    def _get_discharge_port_label(self):
        for obj in self:
            val = "destination"
            if obj.transport and obj.transport != 'air':
                val = 'discharge_port'
            obj.discharge_port_label = val

    #air transport
    transport = fields.Selection( required=True, string='Transport', selection=[(u'land', u'Inland'), (u'ocean', u'Ocean'),(u'air', u'Air')],default='land')
    airline_id = fields.Many2one('res.partner',string='Airline',ondelete='restrict',domain=[('airline','=',True)],context={"default_airline":True})
    flight_no = fields.Char( size=128, string='Flight No')
    tracking_no = fields.Char(size=128, string='Tracking No')
    mwab_date = fields.Date(string='MWAB Date',default=lambda self:fields.Date.today())
    mwab_no = fields.Char(string='MWAB No')
    hwab_no = fields.Char(string="HWAB No",related="name")
    air_issuing_agent_id = fields.Many2one('res.partner', ondelete='restrict', string='Air Issuing Agent',domain=[('agent','=',True)],context={'default_agent':True,'default_customer':True})
    op_date = fields.Date(string="Date",default=lambda self:fields.Date.today())
    load_port_lable = fields.Selection([('gateway', 'Gateway'), ('loading_port', "Loading Port")], compute="_get_loading_port_label")
    discharge_port_label = fields.Selection([('destination', 'Destination'), ('discharge_port', 'Discharge Port')], compute="_get_discharge_port_label")

class FrgOperationInherit(FrgOperation):

	def write(self,vals):
		write_returned = super(FrgOperation,self).write(vals)
		if not self._context.get('test',False):
			for rec in self:
				routings = self.env['frg.carraige'].browse(rec.routings.ids)
				for route in routings:
					if route.rtype == 'main':
						route.write({'dis_port_id':rec.discharge_port_id.id,
							'load_port_id':rec.load_port_id.id,
							'shipping_line_id':rec.shipping_line_id.id,
							'vessel_id':rec.vessel_id.id,
							'airline_id':rec.airline_id.id,
							'flight_no':rec.flight_no,
							'tracking_no':rec.tracking_no
						})						
		return write_returned

	@api.model
	def create(self,vals):
		#print '----------new_op create------------'
		op_rec = super(FrgOperation,self).create(vals)	
		main_route_vals = {
			'rtype':'main',
			'trans_mode': op_rec.transport,
			'load_port_id':op_rec.load_port_id.id,
			'dis_port_id':op_rec.discharge_port_id.id,
			'shipping_line_id':op_rec.shipping_line_id.id or False,
			'trucker_id':op_rec.trucker_id.id or False,
			'vessel_id':op_rec.vessel_id.id or False,
			'voyage_no':op_rec.voy_no,
			'truck_no':op_rec.truck_no,
			'airline_id':op_rec.airline_id.id,
			'flight_no':op_rec.flight_no,
			'tracking_no':op_rec.tracking_no,
			'cutoff_date':op_rec.cutoff_date,
			'frg_operation_id':op_rec.id,
		}
		main_route_rec = self.env['frg.carraige'].create(main_route_vals)
		
		#sequence
		if op_rec.operation_type == 'direct':
			op_rec.name = self.env['ir.sequence'].get('frg.operation')
		elif op_rec.operation_type == 'master':
			op_rec.name = self.env['ir.sequence'].get('frg.master')
		elif op_rec.operation_type == 'house':
			op_rec.name = self.env['ir.sequence'].get('frg.shipment')	
		return op_rec




	@api.onchange('transport')
	def onchange_air(self):
		if self.transport == 'air':
			self.shippment_type = 'LCL'
			for order in self.frg_order_line_ids:
				order.onchange_shippment_type()



	@api.onchange('agent_id')
	def set_master_details(self):
		if self.operation_type == 'master':
			if self.direction == 'export':
				self.shipper_id = self.env.user.company_id.partner_id
				self.consignee_id = self.agent_id
			else:
				self.shipper_id = self.agent_id
				self.consignee_id = self.env.user.company_id.partner_id

			self.air_issuing_agent_id = self.env.user.company_id.partner_id 



	@api.constrains('mwab_no')
	def validate_mwab(self):
		if self.operation_type in ['master','direct'] and self.transport == 'air':
			mwab_no = self.mwab_no
			#check if it's 7 or not 
			if (len(mwab_no) < 8) or (len(mwab_no) > 8):
				raise exceptions.ValidationError('"MWAB No" must be 8 digits!!')
			else:
				if not mwab_no.isdigit():
					raise exceptions.ValidationError('"MWAB No" must be only digits!!')

			#check validation of mwab_no				 
			lastdigit =  int(mwab_no[-1])
			first_7s  =  int(mwab_no[0:7])
			if ((first_7s % 7) != lastdigit):
				raise exceptions.ValidationError('"MWAB No" is not valid!!')



	_sql_constraints = [
		('prefix_uniq', 'UNIQUE (prefix)',  'The Prefix Must be Unique!')
	]		

	def generate_payables(self):
		payable_obj = self.env['freight.payable']
		a = {}
		for route in self.routings:
			for service in self.service_ids:
				if(service.routing_id == route and service.main):
					b = a.get(route.id)
					if(b): a[route.id] += 1
					else: a[route.id] = 1
		if not a:
			raise exceptions.ValidationError("Services doesn't have any main service")
		for key,val in a.items():
			if(val==0):
				raise exceptions.ValidationError("Error: Route "+ str(key) + " doesn't have any main services")
			elif(val>1):
				raise exceptions.ValidationError("Error: Route "+ str(key) + " have more than one main services")

		
		for route in self.routings:
			if route.frg_operation_id.shippment_type == 'FCL':
				service_dict = {}
				if route.route_order_line_ids:
					for order in route.route_order_line_ids:
						if order.package_id.name in service_dict:
							service_dict[order.package_id.name] += 1
						else:
							service_dict[order.package_id.name] = 1		 	

				for service in route.service_ids:
					if not service.payable_ids:
						if not service.lump_sum:
							for package_name,pieces in service_dict.items():
								payable_vals = {
									'name': service.name + " of " + package_name,
									'curr_id': service.curr_id.id, 
									'vendor_id': service.vendor_id.id,
									'operation_payable_id':self.id,
									'price_unit': service.cost, 
									'quantity': pieces,
									'payable_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_expense_id.id,
									'product_id': service.product_id.id,
								}
								created = payable_obj.create(payable_vals)
						else:						
							payable_vals = {
								'name': service.name + " of All containers",
								'curr_id': service.curr_id.id, 
								'vendor_id': service.vendor_id.id,
								'operation_payable_id':self.id,
								'price_unit': service.cost, 
								'quantity': 1,
								'payable_service_ids':[(4,service.id)],
								'account_id': service.product_id.property_account_expense_id.id,
								'product_id': service.product_id.id,
							}
							created = payable_obj.create(payable_vals)	

			if route.frg_operation_id.shippment_type == 'LCL':
				for service in route.service_ids:
					if not service.payable_ids:
						for order in route.route_order_line_ids:
							
							qtys = 1.0
							if service.uom == 'fix':
								qtys = order.pieces
							elif service.uom == 'gw':
								qtys = order.grossw_a
							elif service.uom == 'cw':
								if route.trans_mode == 'land':
									qtys = order.vol_a * VTW_CONV_INLAND
								elif route.trans_mode == 'ocean':
									qtys = order.vol_a * VTW_CONV_OCEAN
								elif route.trans_mode == 'air':
									qtys = order.vol_a * VTW_CONV_AIR

							payable_vals = {
									'name': service.name + " of " + order.package_id.name,
									'curr_id': service.curr_id.id, 
									'vendor_id': service.vendor_id.id,
									'operation_payable_id':self.id,
									'price_unit': service.cost, 
									'quantity': qtys,
									'payable_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_expense_id.id,
									'product_id': service.product_id.id,
								}
							created = payable_obj.create(payable_vals)										
								


	def generate_receivables(self):
		receivable_obj = self.env['freight.receivable']
		a = {}
		for route in self.routings:
			for service in self.service_ids:
				if(service.routing_id==route and service.main):
					b=a.get(route.id)
					if(b): a[route.id]+=1
					else: a[route.id]=1
		if not a:
			raise exceptions.ValidationError("Services doesn't have any main service")
		for key,val in a.items():
			if(val==0):
				raise exceptions.ValidationError("Error: Route "+ str(key) + " doesn't have any main services")
			elif(val>1):
				raise exceptions.ValidationError("Error: Route "+ str(key) + " have more than one main services")


		for route in self.routings:

			if self.shippment_type == 'FCL':
				service_dict = {}
				if route.route_order_line_ids:
					for order in route.route_order_line_ids:
						if order.package_id.name in service_dict:
							service_dict[order.package_id.name] += 1
						else:
							service_dict[order.package_id.name] = 1 	

				for service in route.service_ids:
					if not service.receivable_ids:
						if not service.lump_sum:
							for package_name,pieces in service_dict.items():
								receivable_vals = {
									'name': service.name + " of " + package_name,
									'curr_id': service.curr_id.id, 
									'customer_id': service.vendor_id.id, 
									'operation_receivable_id':self.id,
									'price_unit': service.sale, 
									'quantity': pieces,
									'receive_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_income_id.id,
									'product_id': service.product_id.id,
								}
								created = receivable_obj.create(receivable_vals)
						else:
							receivable_vals = {
								'name': service.name + " of All Containers",
								'curr_id': service.curr_id.id, 
								'customer_id': service.vendor_id.id, 
								'operation_receivable_id':self.id,
								'price_unit': service.sale, 
								'quantity': 1,
								'receive_service_ids':[(4,service.id)],
								'account_id': service.product_id.property_account_income_id.id,
								'product_id': service.product_id.id,
							}
							created = receivable_obj.create(receivable_vals)	

			if self.shippment_type == 'LCL':
				for service in route.service_ids:
					if not service.receivable_ids:
						for order in route.route_order_line_ids:
							qtys = 1.0 
							if service.uom == 'fix':
								qtys = order.pieces
							elif service.uom == 'gw':
								qtys = order.grossw_a
							elif service.uom == 'cw':
								if route.trans_mode == 'land':
									qtys = order.vol_a * VTW_CONV_INLAND
								elif route.trans_mode == 'ocean':
									qtys = order.vol_a * VTW_CONV_OCEAN
								elif route.trans_mode == 'air':
									qtys = order.vol_a * VTW_CONV_AIR

							receivable_vals = {
									'name': service.name + " of " + order.package_id.name,
									'curr_id': service.curr_id.id, 
									'customer_id': service.vendor_id.id, 
									'operation_receivable_id':self.id,
									'price_unit': service.sale, 
									'quantity': qtys,
									'receive_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_income_id.id,
									'product_id': service.product_id.id,
					
								}
							created = receivable_obj.create(receivable_vals)	


	def master_operation_changes(self):
		if self.operation_type == 'master':
			route_obj = self.env['frg.carraige']
			main_route_master  = route_obj.search([('frg_operation_id','=',self.id),('rtype','=','main')])
			for child in self.child_ids:
				child.write({'load_port_id':self.load_port_id.id,'discharge_port_id':self.discharge_port_id.id})
				child.shipping_line_id = self.shipping_line_id
				child.voy_no = self.voy_no
				child.vessel_id = self.vessel_id
				child.note = self.note
				child.trucker_id = self.trucker_id
				child.truck_no = self.truck_no
				child.airline_id = self.airline_id
				child.tracking_no = self.tracking_no
				child.flight_no = self.flight_no
				child.cutoff_date = self.cutoff_date
				for route in child.routings:
					if route.rtype == 'main' and main_route_master:
						route.etd = main_route_master.etd
						route.eta = main_route_master.eta
						route.atd = main_route_master.atd
						route.ata = main_route_master.ata




class ErpReport(models.AbstractModel):
   _name = "report.erp.booking_confirmation"

   def print_report(self):
       docs = {
          'docs1': 'docs1',
          'docs2': 'docs2',
       }
       return self.env['report'].render('erp.report', docs)


class partner(models.Model):
	_inherit = 'res.partner'

	prefix = fields.Integer(string="Prefix",size=3)
	airline_code = fields.Char(string="Airline Code")
	airline = fields.Boolean(string='Airline')
				





