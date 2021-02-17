from odoo import models, fields, api, tools,exceptions, _

VTW_CONV_INLAND = 333.00
VTW_CONV_OCEAN = 1000.00
VTW_CONV_AIR = 167.00

class FrgOperation(models.Model):
	_name = 'frg.operation'
	_rec_name = 'name'
	_order = 'name desc'
	_description = 'Manage Freight Operation'

	routing_state = fields.Char(string='State ',store=True,compute='_set_routing_state')	
	name = fields.Char(string="Name")
	direction = fields.Selection( required=True, string='Direction', selection=[(u'export', u'Export'), (u'import', u'Import')],default='import')
	shippment_type = fields.Selection( required=True, string='Shippment Type', selection=[(u'FCL', u'FCL'), (u'LCL', u'LCL')],default='FCL')	
	consignee_id = fields.Many2one('res.partner', ondelete='restrict', string='Consignee',domain=[('consignee','=',True)],context={'default_consignee':True,'default_customer':True})
	agent_id = fields.Many2one('res.partner', ondelete='restrict', string='Agent',domain=[('agent','=',True)],context={'default_agent':True,'default_customer':True})
	transport = fields.Selection( required=True, string='Transport', selection=[(u'land', u'Inland'), (u'ocean', u'Ocean')],default='land')
	shipping_line_id = fields.Many2one('res.partner', ondelete='restrict', string='Shipping Line',domain=[('shipping_line','=',True)],context={'default_shipping_line':True})	
	trucker_id = fields.Many2one('res.partner', ondelete='restrict', string='Trucker',domain=[('trucker','=',True)],context={'default_trucker':True})
	my_customer = fields.Selection( required=False, string='My Customer', selection=[(u'consignee', u'Consignee'), (u'shipper', u'Shipper')],compute='_compute_my_customer',)
	shipper_id = fields.Many2one('res.partner', ondelete='restrict', string='Shipper',domain=[('shipper','=',True)],context={'default_shipper':True,'default_customer':True})
	discharge_port_id = fields.Many2one('frg.port', ondelete='restrict', required=True,string="Discharge Port")
	load_port_id = fields.Many2one('frg.port', ondelete='restrict', required=True,string='Loading Port')
	vessel_id = fields.Many2one('frg.vessel', ondelete='set null', string='Vessel',)
	voy_no = fields.Char( size=128, string='Voyage No',)
	truck_no = fields.Char( string='Truck No',)
	frg_order_line_ids = fields.One2many('frg.order.line', 'frg_operation_id', required=True, string='Order lines',)
	cutoff_date = fields.Datetime( string='Cut Off Date',)
	book_no = fields.Char( size=128, string='Booking No',)
	note = fields.Text( string='Notes',)
	ref = fields.Char( string='Reference1',)
	freight_pc = fields.Selection( required=True, string='Operation Payment', selection=[(u'collect', u'Collect'), (u'prepaid', u'Prepaid')],)
	user_id = fields.Many2one('res.users', ondelete='restrict', required=True, string='Operator',default=lambda self: self.env.uid)
	booking_confirm_no = fields.Integer(string="Booking Confirmation No#")
	frg_order_line_extended_ids = fields.One2many('frg.order.line.extended', 'frg_operation_id',string="Containers")
	payable_ids = fields.One2many('freight.payable','operation_payable_id',ondelete='cascade')
	receivable_ids = fields.One2many('freight.receivable','operation_receivable_id',ondelete='cascade')
	service_ids = fields.One2many(string='Services', comodel_name='frg.service', inverse_name='operation_id')
	routings = fields.One2many(string='Routings', comodel_name='frg.carraige', inverse_name='frg_operation_id')	
	containers_sum = fields.Integer(compute='get_number_of_containers')
	containers_generated = fields.Boolean(store=True)
	master_generated = fields.Boolean(string="Master ordered generated")
	bl_number = fields.Char(string="B/L No")
	total_vol = fields.Float(string="Total Volume",store=True,compute="get_total_weight_vol")
	total_weight = fields.Float(string="Total Weight:",compute="get_total_weight_vol")
	total_orders = fields.Integer(string="Total Weight:",compute="get_total_weight_vol")	
	#invoicing part
	total_payables = fields.Float(string='Total payables',store=True,compute='_get_total_payables')
	total_receivables = fields.Float(string='Total receivables',store=True,compute='_get_total_receivables')
	total_payables_btn = fields.Float(string='Total payables',store=True,compute='_get_total_payables')
	total_receivables_btn = fields.Float(string='Total receivables',store=True,compute='_get_total_receivables')
	total_invoiced_payables = fields.Float(string='Total invoiced payables',store=True,compute='_get_total_invoiced_payables')
	total_invoiced_receivables = fields.Float(string='Total invoiced receivables',store=True,compute='_get_total_invoiced_receivables')	
	payables_amount_due = fields.Float(string="Payables Amount Due",store=True,compute='_get_payables_amount_due')
	receivables_amount_due = fields.Float(string="Receivables Amount Due",store=True,compute='_get_receivables_amount_due')
	payables_amount_paid = fields.Float(string="Payables Amount Paid",store=True,compute="_get_payables_amount_due")
	receivables_amount_paid = fields.Float(string="Receivables Amount Paid",store=True,compute='_get_receivables_amount_due')
	expected_profit = fields.Float(string="Expected Profit",store=True,compute="compute_expected_profit")
	actual_profit = fields.Float(string="Actual Profit",store=True,compute="compute_actual_profit")
	main_currency = fields.Char(compute='get_currency')
	payable_no  = fields.Integer('Number of Payable',compute='_get_total_payables',default=0)
	recv_no  = fields.Integer('Number of Recievalble',compute='_get_total_receivables',default=0)	
	#house and master part
	operation_type = fields.Selection([(u'direct',u'Direct'),(u'master',u'Master'),(u'house',u'House')],default='direct')
	parent_id = fields.Many2one('frg.operation',string="Master Operation")
	child_ids = fields.One2many('frg.operation','parent_id',string="Shipments")
	master_orders_extended = fields.One2many('frg.order.line.extended', 'master_operation_id',string="Containers")
	#overview Cargo
	total_gross_a  = fields.Float(string="Total Actual Gross Weight",compute='_calc_total_gross_weight')
	total_vol_a  = fields.Float(string="Total Actual Volume",compute='_calc_total_gross_weight')
	total_qty_a  = fields.Integer(string="Pieces",compute='_calc_total_gross_weight')


	@api.depends('frg_order_line_extended_ids','frg_order_line_extended_ids.vol_a','frg_order_line_extended_ids.grossw_a','master_orders_extended','master_orders_extended.vol_a','master_orders_extended.grossw_a')
	def _calc_total_gross_weight(self):
		total_vol = 0.0
		total_gross = 0.0
		total_qty = 0
		if self.operation_type in ['house','direct']:
			for package in self.frg_order_line_extended_ids:
				total_vol += package.vol_a
				total_gross += package.grossw_a
				total_qty += package.pieces
		else:
			for package in self.master_orders_extended:
				total_vol += package.vol_a
				total_gross += package.grossw_a
				total_qty += package.pieces

		self.total_gross_a = total_gross
		self.total_vol_a = total_vol
		self.total_qty_a = total_qty


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
				child.cutoff_date = self.cutoff_date
				for route in child.routings:
					if route.rtype == 'main' and main_route_master:
						route.etd = main_route_master.etd
						route.eta = main_route_master.eta
						route.atd = main_route_master.atd
						route.ata = main_route_master.ata
		


	def get_currency(self):
		self.main_currency = self.env.user.company_id.currency_id.name

	@api.depends('frg_order_line_ids','frg_order_line_ids.qty','frg_order_line_extended_ids')
	def get_number_of_containers(self):
		total = 0
		for rec in self.frg_order_line_ids:
			total += rec.qty
		self.containers_sum = total												
	

	# invoicing part
	@api.depends('payable_ids','payable_ids.price_unit','payable_ids.curr_id','payable_ids.quantity')
	def _get_total_payables(self):
		self.payable_no = len(self.payable_ids)		
		total=0
		for payable in self.payable_ids:
			main_currency = self.env.user.company_id.currency_id
			amount = payable.curr_id.compute(payable.price_unit,main_currency)
			total += amount*payable.quantity

		self.total_payables = total
		self.total_payables_btn = total

	@api.depends('receivable_ids','receivable_ids.quantity','receivable_ids.curr_id','receivable_ids.price_unit')
	def _get_total_receivables(self):
		self.recv_no = len(self.receivable_ids)		
		total=0
		for receivable in self.receivable_ids:
			main_currency = self.env.user.company_id.currency_id
			amount = receivable.curr_id.compute(receivable.price_unit,main_currency)
			total += amount*receivable.quantity

		self.total_receivables=total
		self.total_receivables_btn = total

	@api.depends('payable_ids.move_id','payable_ids.price_unit','payable_ids.curr_id','payable_ids.quantity')
	def _get_total_invoiced_payables(self):
		total=0
		for payable in self.payable_ids:
			if payable.move_id:
				main_currency = self.env.user.company_id.currency_id
				amount = payable.curr_id.compute(payable.price_unit,main_currency)
				total += amount*payable.quantity

		self.total_invoiced_payables=total


	@api.depends('receivable_ids.move_id','receivable_ids.quantity','receivable_ids.curr_id','receivable_ids.price_unit')
	def _get_total_invoiced_receivables(self):
		total=0
		for receivable in self.receivable_ids:
			if receivable.move_id:
				main_currency = self.env.user.company_id.currency_id
				amount = receivable.curr_id.compute(receivable.price_unit,main_currency)
				total += amount*receivable.quantity
		self.total_invoiced_receivables=total

	@api.depends('payable_ids','payable_ids.move_id.amount_residual','payable_ids.move_id','payable_ids.move_id.amount_total','payable_ids.move_id.state')
	def _get_payables_amount_due(self):
		total_amount_due = 0
		total_amount_paid = 0
		payablesWithTheSameInvoiceID = []
		for payable in self.payable_ids:
			if payable.move_id:
				if payable.move_id not in payablesWithTheSameInvoiceID:
					payablesWithTheSameInvoiceID.append(payable.move_id)

		for unique_payable_invoice in payablesWithTheSameInvoiceID:
			if unique_payable_invoice.state in ['open','paid']:
				total_amount_due += unique_payable_invoice.amount_residual
				total_amount_paid += unique_payable_invoice.amount_total - unique_payable_invoice.amount_residual
		self.payables_amount_due = total_amount_due
		self.payables_amount_paid = total_amount_paid						

	@api.depends('receivable_ids','receivable_ids.move_id','receivable_ids.move_id.amount_residual','receivable_ids.move_id.amount_total','receivable_ids.move_id.state')
	def _get_receivables_amount_due(self):
		total_amount_due = 0
		total_amount_paid = 0
		receivablesWithTheSameInvoiceID = []
		for receivable in self.receivable_ids:
			if receivable.move_id:
				if receivable.move_id not in receivablesWithTheSameInvoiceID:
					receivablesWithTheSameInvoiceID.append(receivable.move_id)

		for unique_receivable_invoice in receivablesWithTheSameInvoiceID:
			if unique_receivable_invoice.state in ['open','paid']:			
				total_amount_due += unique_receivable_invoice.amount_residual
				total_amount_paid += unique_receivable_invoice.amount_total - unique_receivable_invoice.amount_residual

		self.receivables_amount_due = total_amount_due
		self.receivables_amount_paid = total_amount_paid

	@api.depends('total_payables','total_receivables')
	def	compute_expected_profit(self):
		self.expected_profit = self.total_receivables - self.total_payables

	@api.depends('total_invoiced_payables','total_invoiced_receivables')
	def compute_actual_profit(self):
		self.actual_profit = self.total_invoiced_receivables - self.total_invoiced_payables	
	# end invoicing part


	@api.depends('frg_order_line_ids.gross_w','frg_order_line_ids.vol','frg_order_line_ids.qty')
	def get_total_weight_vol(self):
		total_weight = 0
		total_vol    = 0
		total_orders = 0
		for rec in self.frg_order_line_ids:
			total_weight += rec.gross_w
			total_vol    += rec.vol
			total_orders += rec.qty

		self.total_weight    = total_weight			
		self.total_vol       = total_vol		
		self.total_orders    = total_orders			



	def _compute_my_customer(self):
		self.my_customer = False


	@api.depends('routings','routings.atd','routings.ata')
	def _set_routing_state(self):
		routing_rec = self.env['frg.carraige'].search([('frg_operation_id','=',self.id)])
		if not self.routings:
			self.routing_state = 'Draft'
		else:
			self.routing_state = 'Ordered'	
		
		for route in routing_rec:
			if route.atd and route.atd <= fields.Datetime().now() and route.rtype == 'pickup':
				self.routing_state = 'Pickup'
			if route.ata and route.ata <= fields.Datetime().now() and route.rtype == 'pickup':
				self.routing_state = 'On Hand'
			if route.atd and route.atd <= fields.Datetime().now() and route.rtype == 'precar':
				self.routing_state = '[PRE]Departed from '+ route.load_port_id.name
			if route.ata and route.ata <= fields.Datetime().now() and route.rtype == 'precar':
				self.routing_state = '[PRE]Arrived to '+ route.dis_port_id.name								
			if route.atd and route.atd <= fields.Datetime().now() and route.rtype == 'main':
				self.routing_state = '[MAIN]Departed from '+ route.load_port_id.name
			if route.ata and route.ata <= fields.Datetime().now() and route.rtype == 'main':
				self.routing_state = '[MAIN]Arrived to '+ route.dis_port_id.name
			if route.atd and route.atd <= fields.Datetime().now() and route.rtype == 'oncar':
				self.routing_state = '[ON]Departed from '+ route.load_port_id.name
			if route.ata and route.ata <= fields.Datetime().now() and route.rtype == 'oncar':
				self.routing_state = '[ON]Arrived to '+ route.dis_port_id.name				
			if route.atd and route.atd <= fields.Datetime().now() and route.rtype == 'delivery':
				self.routing_state = 'Delivery'
			if route.ata and route.ata <= fields.Datetime().now() and route.rtype == 'delivery':
				self.routing_state = 'Delivered'				


	@api.model		
	def create(self,vals):
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
		

	def write(self,vals):
		write_returned = super(FrgOperation,self).write(vals)
		#print '-------write(op_old)----------',vals		
		if not self._context.get('test',False):
			#print '------------exe----------'
			for rec in self:
				routings = self.env['frg.carraige'].browse(rec.routings.ids)
				for route in routings:
					if route.rtype == 'main':
						route.write({'dis_port_id':rec.discharge_port_id.id,'load_port_id':rec.load_port_id.id,'shipping_line_id':rec.shipping_line_id.id,'vessel_id':rec.vessel_id.id})						
		return write_returned	


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
					move_id = self.env['account.move'].with_context(default_partner_id=service.vendor_id.id, default_type="in_invoice").new()
					move_id = self.env['account.move'].create(move_id._cache)
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
									'move_id': move_id.id
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
								'move_id': move_id.id

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
						move_id = self.env['account.move'].with_context(default_partner_id=service.vendor_id.id, default_type="out_invoice").new()
						move_id = self.env['account.move'].create(move_id._cache)
						if not service.lump_sum:
							for package_name,pieces in service_dict.items():
								receivable_vals = {
									'name': service.name + " of " + package_name,
									'curr_id': service.curr_id.id, 
									'operation_receivable_id':self.id,
									'price_unit': service.sale, 
									'quantity': pieces,
									'receive_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_income_id.id,
									'product_id': service.product_id.id,
									'move_id': move_id.id,
								}
								created = receivable_obj.create(receivable_vals)
						else:
							receivable_vals = {
								'name': service.name + " of All Containers",
								'curr_id': service.curr_id.id, 
								'operation_receivable_id':self.id,
								'price_unit': service.sale, 
								'quantity': 1,
								'receive_service_ids':[(4,service.id)],
								'account_id': service.product_id.property_account_income_id.id,
								'product_id': service.product_id.id,
								'move_id': move_id.id,
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

							receivable_vals = {
									'name': service.name + " of " + order.package_id.name,
									'curr_id': service.curr_id.id, 
									'operation_receivable_id':self.id,
									'price_unit': service.sale, 
									'quantity': qtys,
									'receive_service_ids':[(4,service.id)],
									'account_id': service.product_id.property_account_income_id.id,
									'product_id': service.product_id.id,
									'invoice_line_id':self.id,

					
								}
							created = receivable_obj.create(receivable_vals)					

				
	def generate_from_orders(self):
		order_line_extended_obj = self.env['frg.order.line.extended']

		if self.shippment_type == 'FCL' and self.operation_type in ['house','direct']:
			if not self.containers_generated:
				for order in self.frg_order_line_ids:
					order_extended_vals = {
						'package_id': order.package_id.id,
						'vol': order.vol,
						'gross_w': order.gross_w,
						'frg_operation_id':self.id,
						'master_operation_id':self.parent_id.id or False,
						'operation_type_new':order.operation_type_new
					}
					quantity_iterator = order.qty		
					for rec in range(0,quantity_iterator):
						order_line_extended_obj.create(order_extended_vals)
			self.containers_generated = True		



		if self.shippment_type == 'LCL' and self.operation_type in ['house','direct']:			
			if not self.containers_generated:
				for order in self.frg_order_line_ids:
					order_extended_vals = {
						'package_id': order.package_id.id,
						'vol': order.vol,
						'gross_w': order.gross_w,
						'frg_operation_id':self.id,
						'master_operation_id':self.parent_id.id or False,
						'operation_type_new':order.operation_type_new,
						'pieces':order.qty,

					}
				
					order_line_extended_obj.create(order_extended_vals)
			self.containers_generated = True

		if self.operation_type == 'master':
			for child in self.child_ids:
				if not child.containers_generated:
					child.generate_from_orders()
					child.master_generated = True		
			#deleting master orders				
			for order in self.frg_order_line_ids:
				order.unlink()

	@api.constrains('load_port_id','discharge_port_id')
	def check_ports(self):
		if self.load_port_id and self.load_port_id == self.discharge_port_id and self.discharge_port_id:
			raise exceptions.ValidationError("From and To Port Can't be the same")

	
	def open_payable(self):
		self.ensure_one()
		 
		domain = [('operation_payable_id','=',self.id)]
		search_view_id = self.env.ref('freight_management.payable_search_view').id or False
		payable_action = {
			'name': 'Payables',
			'view_mode':'tree,form',
			'src_model':'frg.operation',
			'view_type':'form',
			'res_model': 'freight.payable',
			'type': 'ir.actions.act_window',
			'target':'current',
			'domain':domain,
			'search_view_id':search_view_id,
			'context':{'default_operation_payable_id':self.id,'search_default_group_by_vendor':1,'search_default_group_by_currency':1}			
		}
		return payable_action


	def open_receivable(self):
		self.ensure_one()
		domain = [('operation_receivable_id','=',self.id)]
		search_view_id = self.env.ref('freight_management.recev_search_view').id or False
		receivable_action = {
			'name': 'Receivables',
			'view_mode':'tree,form',
			'src_model':'frg.operation',
			'view_type':'form',
			'res_model':'freight.receivable',
			'type': 'ir.actions.act_window',
			'target':'current',
			'domain':domain,
			'search_view_id':search_view_id,
			'context':{'default_operation_receivable_id':self.id,'search_default_group_by_currency':1}
		}
		return receivable_action


	@api.onchange('agent_id')
	def set_master_default_details(self):
		if self.operation_type == 'master':
			if self.direction == 'export':
				self.shipper_id = self.env.user.company_id.partner_id
				self.consignee_id = self.agent_id 
			else:
				self.shipper_id = self.agent_id
				self.consignee_id = self.env.user.company_id.partner_id

	def deattach_house(self):
		self.parent_id = False
		for order_line in self.frg_order_line_extended_ids:
			order_line.master_operation_id = False
		return {
		    'type': 'ir.actions.client',
		    'tag': 'reload',
		}

	def de_attach_all(self):
		for child in self.child_ids:
			child.deattach_house()									

		


class FrgOrderLine(models.Model):
	_name = 'frg.order.line'
	_description = 'Order Lines'
	gross_w = fields.Float( digits=(16, 3), string='Expected Gross Weight(KG)')
	discription = fields.Text(string="Description Of Goods")
	frg_operation_id = fields.Many2one('frg.operation', ondelete='restrict', string='Freight Operation',)
	qty = fields.Integer( required=True,default=1)
	package_id = fields.Many2one('frg.package', ondelete='restrict', required=True, string='Container',)
	vol = fields.Float( digits=(16, 3), string=' Expected Volume(CBM)',help="Volume in Cubic Meter")
	operation_type_new = fields.Selection([('dry','Dry'),('reefer','Reefer')],default='dry',string="Operation Type")		
	container = fields.Boolean('Is Container?',related='package_id.container')


	shippment_type = fields.Selection( required=True, string='Shippment Type', selection=[(u'FCL', u'FCL'), (u'LCL', u'LCL')],related='frg_operation_id.shippment_type')

	@api.onchange('shippment_type')
	def onchange_shippment_type(self):
		if self.shippment_type == 'LCL':
			return {'domain':{'package_id': [('container', '=', False)]}} 
		if self.shippment_type == 'FCL':
			return {'domain':{'package_id': [('container', '=', True)]}}



class FrgOrderLineExnteded(models.Model):
	_inherit = 'frg.order.line'
	_name = 'frg.order.line.extended'
	pieces = fields.Integer(string="Pieces",default=1,readonly=False)
	container_no = fields.Char(string="Container No#",size=11)
	seal = fields.Char(string='Seal')
	temperature = fields.Integer(string="Temperature")
	ventilation = fields.Float(string="Ventilation",digits=(16,2))
	frg_operation_id = fields.Many2one('frg.operation', ondelete='restrict', string='Freight Operation',)	
	master_operation_id = fields.Many2one('frg.operation', ondelete='restrict', string='Master Operation',)	
	parent_id = fields.Many2one('frg.order.line.extended',string='Packages')
	child_ids = fields.One2many('frg.order.line.extended','parent_id',string='Packages')
	grossw_a = fields.Float(digits=(9,2), string='Gross Weight(KG)',store=True,compute='compute_weight')
	vol_a = fields.Float(digits=(9,2), string='Volume(CBM)',store=True,compute='compute_vol',help="Volume in Cubic Meter")
	route_order_line_ids = fields.Many2many('frg.carraige','route_order_line',string='Route Order Lines')
	valid = fields.Boolean('Is Valid',compute='_is_valid')
	generated = fields.Boolean(string='Generated',default=False)

	manual_gross = fields.Float(digits=(9,2), string='Gross Weight(KG)')
	manual_vol = fields.Float(digits=(9,2), string='Volume(CBM)')
	
	@api.depends('container_no')
	def _is_valid(self):
		for r in self:
			if r.container_no and len(r.container_no) == 11:
				k = r.container_no
				s = 0.0
				for i in range(0,10):
					if i <= 3:
						s = s + (((int(11 * (ord(k[i:i+1]) - 56)) / 10) + 1) * (2 ** ((i+1) - 1)))	
					else:
						s = s + (((ord(k[i:i+1]) - 48)) * (2 ** ((i+1) - 1)))		
				ISO6346Check = (s - int(s / 11) * 11) % 10
				if str(ISO6346Check) != str(float(k[-1:])):
					r.valid = False
				else:
					r.valid = True
			else:
				r.valid = False



	def unlink(self):
		for r in self:
			if r.route_order_line_ids:
				raise exceptions.ValidationError("Can't delete this order line it's related with routing")
		return super(FrgOrderLineExnteded, self).unlink()
		


	@api.depends('child_ids.manual_gross','child_ids','manual_gross')
	def compute_weight(self):
		for obj in self:
			total_weight = 0
			if obj.child_ids:
				for child in obj.child_ids:
					total_weight += child.manual_gross
				obj.grossw_a = total_weight
			else:
				obj.grossw_a = obj.manual_gross

	


	@api.depends('child_ids.manual_vol','child_ids','manual_vol')
	def compute_vol(self):
		for obj in self:
			total_volume = 0
			if obj.child_ids:
				for child in obj.child_ids:
					total_volume += child.manual_vol
				obj.vol_a = total_volume
			else:
				obj.vol_a = obj.manual_vol





class FrgPackage(models.Model):
	_name = 'frg.package'
	_rec_name = 'name'
	_description = 'Package'
	name = fields.Char( string='Name',required=True)
	land = fields.Boolean( string='Inland?',)
	container = fields.Boolean( string='Is container?',default=True)
	code = fields.Char( string='Code',)
	size = fields.Integer( string='Size',)
	active = fields.Boolean( string='Active',default=True)
	vol = fields.Float( digits=(16, 3), string='Volume(CBM)',help="Volume in Cubic Meter")
	ocean = fields.Boolean( string='Ocean?',)
	
	

class FrgPort(models.Model):
	_name = 'frg.port'
	_rec_name = 'name'
	_description = 'Ports'
	country_id = fields.Many2one('res.country', ondelete='restrict', string='Country')
	code = fields.Char( size=128, required=True, string='Code',)
	name = fields.Char( required=True, string='Name',)
	note = fields.Text( string='Note',)
	ocean = fields.Boolean( string='Ocean?',)
	land = fields.Boolean( string='Inland?',)
	active = fields.Boolean( string='Active',default=True)
	state_id = fields.Many2one('res.country.state', ondelete='restrict', string='State',domain="[('country_id','=',country_id.id)]")
	
	


class FrgVessel(models.Model):
	_name = 'frg.vessel'
	_rec_name = 'name'
	_description = 'Vessel'
	active = fields.Boolean( string='Active',default=True)
	note = fields.Text( string='Note',)
	name = fields.Char( required=True, string='Name',)
	code = fields.Char( string='Code',)
	


class ResPartner(models.Model):
	_name = 'res.partner'
	_inherit = [
		'res.partner',
		
	]
	_description = 'Partner'
	agent = fields.Boolean( string='Agent',)
	trucker = fields.Boolean( string='Trucker',)
	shipping_line = fields.Boolean( string='Shipping Line',)
	shipper = fields.Boolean( string='Shipper',)
	consignee = fields.Boolean( string='Consignee',)
	


	
class shippments_wizard(models.TransientModel):
	_name = 'shippments.wizard'

	def _get_master(self):
		master_id = self.env['frg.operation'].browse(self._context.get('active_id'))
		return master_id		

	master_id = fields.Many2one('frg.operation',string='Master operation',default=_get_master)
	shippment_ids = fields.Many2many('frg.operation',string="Shippments")
	

	@api.onchange('master_id')
	def set_shippment_domain(self):
		domain = [('operation_type','=','house'),('parent_id','=',False)]
		domain_state = ['|','|','|','|','|',('routing_state','ilike','Draft'),('routing_state','ilike','Ordered'),('routing_state','ilike','Pickup'),('routing_state','ilike','On Hand'),('routing_state','ilike','[PRE]Departed'),('routing_state','ilike','[PRE]Arrived')]
		domain_transport = ('transport','=',self.master_id.transport)
		domain_direction = ('direction','=',self.master_id.direction)
		domain_load = ('load_port_id','=',self.master_id.load_port_id.id)
		domain_discharge = ('discharge_port_id','=',self.master_id.discharge_port_id.id)
		domain_shippment_type = ('shippment_type','=',self.master_id.shippment_type)
				
		if self.master_id.transport == 'ocean':
			domain_shipping_line_id = ('shipping_line_id','=',self.master_id.shipping_line_id.id)
			domain_vessel_id = ('vessel_id','=',self.master_id.vessel_id.id)
			domain.append(domain_transport)
			domain.append(domain_direction)
			domain.append(domain_load)
			domain.append(domain_discharge)
			domain.append(domain_shipping_line_id)
			domain.append(domain_vessel_id)
			domain.append(domain_shippment_type)
		else:
			domain_trucker_id = ('trucker_id','=',self.master_id.trucker_id.id)
			domain.append(domain_transport)
			domain.append(domain_direction)
			domain.append(domain_load)
			domain.append(domain_discharge)
			domain.append(domain_trucker_id)
			domain.append(domain_shippment_type)
		domain = domain + domain_state						
		return {'domain':{'shippment_ids':domain}}


	def attach_shippment(self):
		for house in self.shippment_ids:
			house.parent_id = self.master_id
			for order_line in house.frg_order_line_extended_ids:
				order_line.master_operation_id = self.master_id
