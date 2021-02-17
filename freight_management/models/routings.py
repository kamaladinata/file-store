from odoo import models, fields, api,exceptions
from odoo.tools.translate import _

class FrgCarraige(models.Model):
	_name = 'frg.carraige'
	_rec_name='name'
	_description = 'Freight Carriage Operations'
	_order = "sequence asc,id asc"


	def _get_type(self):
		selection = [
		  (u'delivery', u'Delivery'), 
		  (u'oncar', u'On-Carraige'),
		  (u'pickup', u'Pickup'),
		  (u'precar', u'Pre-Carraige'),
		  (u'main', u'Main Carraige')
		] 

		op_id = self._context.get('default_frg_operation_id',False)
		if op_id:
			op_rec = self.env['frg.operation'].browse(op_id)
			if op_rec.operation_type == 'master':
				selection = [
				  (u'pickup', u'Pickup'),				
				  (u'delivery', u'Delivery'), 
				  (u'main', u'Main Carraige')				
				]
			rlist = [] #operation route list
			for route in op_rec.routings:
				if route.rtype not in ['pickup','delivery'] :rlist.append(route.rtype)
			for r in rlist:
				for s in selection:
					if r  == s[0]: selection.remove(s)
		return selection


	name = fields.Char(string="Name")
	vessel_id = fields.Many2one('frg.vessel', ondelete='restrict', string='Vessel',)
	trucker_id = fields.Many2one('res.partner', ondelete='restrict', string='Trucker',domain=[('trucker','=',True)],context={'default_trucker':True})
	truck_no = fields.Char( string='Truck No',)
	etd = fields.Datetime( string='ETD',)
	eta = fields.Datetime( string='ETA',)
	atd = fields.Datetime( string='ATD')
	ata = fields.Datetime( string='ATA')
	driver = fields.Char( string='Driver')
	to = fields.Selection( string='To', selection=[(u'port', u'Port'), (u'add', u'Address')],default='port')
	from_dst = fields.Selection( string='From', selection=[(u'port', u'Port'), (u'add', u'Address')],default='port')
	cutoff_date = fields.Date( string='CutOff',)
	voyage_no = fields.Char( string='Voyage No:',)
	shipping_line_id = fields.Many2one('res.partner', ondelete='restrict', string='Shipping Line',domain=[('shipping_line','=',True)],context={'default_shipping_line':True})
	dis_port_id = fields.Many2one('frg.port', ondelete='restrict', string='Discharge Port',)
	load_port_id = fields.Many2one('frg.port', ondelete='restrict', string='Loading Port',)
	trans_mode = fields.Selection( required=True, string='Trans Mode', selection=[(u'ocean', u'Ocean'), (u'land', u'Inland')])
	rtype = fields.Selection( required=True, string='Type', selection=[(u'delivery', u'Delivery'), (u'oncar', u'On-Carraige'), (u'pickup', u'Pickup'), (u'precar', u'Pre-Carraige'), (u'main', u'Main Carraige')])#_get_type
	to_street = fields.Char( string='Street',)
	to_city = fields.Char(string='City',)
	to_country_id = fields.Many2one('res.country', ondelete='restrict', string='Country',)
	to_state_id = fields.Many2one('res.country.state', ondelete='restrict', string='State',)
	from_country_id = fields.Many2one('res.country', ondelete='restrict', string='Country',)
	from_state_id = fields.Many2one('res.country.state', ondelete='restrict', string='State',)
	from_city = fields.Char( string='City',)
	from_street = fields.Char(string='Street')
	frg_operation_id = fields.Many2one(string='Operation', required=True,comodel_name='frg.operation', ondelete='cascade')
	operation_type = fields.Selection(string="Operation Type",related="frg_operation_id.operation_type")
	sequence = fields.Integer(string='Sequence', compute = '_set_seq', store=True, default=0, )
	route_order_line_ids = fields.Many2many('frg.order.line.extended','route_order_line',string='Order lines')
	service_ids = fields.One2many('frg.service','routing_id',string="Services",ondelete="cascade")



	@api.constrains('atd','ata','etd','eta')
	def atd_constrain(self):
		for rec in self:
			precar_rec    = rec.search([('rtype','=','precar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			oncar_rec     = rec.search([('rtype','=','oncar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			main_rec      = rec.search([('rtype','=','main'),('frg_operation_id','=',rec.frg_operation_id.id)])
			pickup_rec    = rec.search([('rtype','=','pickup'),('frg_operation_id','=',rec.frg_operation_id.id)])
			delivery_rec  = rec.search([('rtype','=','delivery'),('frg_operation_id','=',rec.frg_operation_id.id)])
			if(precar_rec.ata and main_rec.atd and precar_rec.ata > main_rec.atd):
				raise exceptions.ValidationError("PreCarriage Arrival time must be less than Main carriage Departure time")

			if(precar_rec.atd and main_rec.atd and precar_rec.atd > main_rec.atd):
				raise exceptions.ValidationError("PreCarriage Departure time must be less than Main carriage Departure time")

			if(oncar_rec.atd and main_rec.ata and oncar_rec.atd < main_rec.ata or (oncar_rec.atd or oncar_rec.ata and (not main_rec.ata or not main_rec.atd))):
				raise exceptions.ValidationError("OnCarriage Departure time must be less than Main carriage Departure time")

			for pickup in pickup_rec:
				if(pickup.ata and precar_rec.atd and pickup.ata > precar_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Arrival time must be less than PreCarriage Departure time")
				if(pickup.ata  and main_rec.atd and pickup.ata > main_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Arrival time must be less Main carriage Departure time")
				if(pickup.ata and oncar_rec.atd and pickup.ata > oncar_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Arrival time more than OnCarriage Departure time")

				if(pickup.atd and precar_rec.atd and pickup.atd > precar_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Departure time must be less than PreCarriage Departure time")
				if(pickup.atd and main_rec.atd and pickup.atd > main_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Departure time must be less Main carriage Departure time")
				if(pickup.atd and oncar_rec.atd and pickup.atd > oncar_rec.atd):
					raise exceptions.ValidationError("Pickup " + str(pickup.id)+" Departure time more than OnCarriage Departure time")
			
			for delivery in delivery_rec:
				if(delivery.atd and precar_rec.ata and delivery.atd < precar_rec.ata):
					raise exceptions.ValidationError("Delivery Departure time must be greater than Precarriage Arrival time")
				if(delivery.atd and main_rec.ata and delivery.atd < main_rec.ata):
					raise exceptions.ValidationError("Delivery Departure time must be greater than Main Arrival time")
				if(delivery.atd and oncar_rec.ata and delivery.atd < oncar_rec.ata):
					raise exceptions.ValidationError("Delivery departure time must be greater than Oncarriage Arrival time")


	@api.constrains('atd','ata','etd','eta')
	def check_route_time(self):
		for rec in self:
			if (rec.ata < rec.atd and rec.ata and rec.atd) or (rec.eta < rec.etd and rec.eta and rec.etd):
				raise exceptions.ValidationError(rec.rtype + " departure time must be less than " + rec.rtype + " Arrival time")


	@api.constrains('service_ids')
	def check_services(self):
		for rec in self:
			if rec.service_ids:
				main_count = 0 
				for service in rec.service_ids:
					if service.main : main_count += 1
				if main_count == 0 :
					raise exceptions.ValidationError("Error: Route "+ rec.name + " doesn't have any main services")
				if main_count > 1:
					raise exceptions.ValidationError("Error: Route "+ rec.name + " does have more than main service")
	

	def unlink(self):
		for r in self:
			if r.rtype =='main' and r.frg_operation_id:
				raise exceptions.ValidationError("Can't delete Main carraige of operation")
		return super(FrgCarraige, self).unlink()


	@api.depends('rtype')
	def _set_seq(self):
		mapped_dic = {
		'pickup':0,
		'precar':1,
		'main':2,
		'oncar':3,
		'delivery':4,
		}
		for r in self: 
			r.sequence = mapped_dic.get(r.rtype,0)


	def port_name_errors(self):
		if self.rtype == 'precar':
			return "From and To Port Can't be the same in port 'Pre carriage'"
		elif self.rtype == 'oncar':
			return "From and To Port Can't be the same in port 'On Carriage'"
		elif self.rtype == 'main':
			return "From and To Port Can't be the same in port 'Main Carriage'"
		elif self.rtype == 'pickup':
			return "From and To Port Can't be the same in port 'Pickup'"
		elif self.rtype == 'delivery':
			return "From and To Port Can't be the same in port 'Delivery'"	


	@api.constrains('load_port_id','dis_port_id')
	def check_ports(self):
		if self.load_port_id and self.load_port_id == self.dis_port_id and self.dis_port_id:
			raise exceptions.ValidationError(self.port_name_errors())


	@api.constrains('rtype','frg_operation_id')
	def check_type_uniquness(self):
		if self.rtype in ['main','oncar','precar']:
			for route in self.frg_operation_id.routings:
				if route.id != self.id and route.rtype == self.rtype:
					err_msg = "Can't have more than one of Carriage type of " + self.rtype + " Per Operation"
					raise exceptions.ValidationError(err_msg)

	@api.onchange('rtype')
	def onchange_type(self):
		if self.rtype in ['pickup','delivery']:
			self.trans_mode = 'land'
		elif self.rtype == 'precar':
			self.dis_port_id = self.frg_operation_id.load_port_id or False
		elif self.rtype == 'oncar':
			self.load_port_id = self.frg_operation_id.discharge_port_id or False


	@api.model
	def create(self,vals):
		route_rec = super(FrgCarraige,self).create(vals)
		route_rec.name = self.env['ir.sequence'].get('frg.routing')
		return route_rec		


	def write(self,vals):
		write_returned = super(FrgCarraige,self).write(vals)
		#print '--------write(route old)-----------',vals
		copied_context = self._context.copy()
		copied_context.update({'test':True})
		for rec in self:
			#print '------------exe----------'
			precar_rec = rec.search([('rtype','=','precar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			oncar_rec  = rec.search([('rtype','=','oncar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			if rec.rtype == 'main':
				op_rec = self.env['frg.operation'].browse(rec.frg_operation_id.id)
				op_rec_new_context = op_rec.with_context(copied_context)
				op_rec_new_context.write({'discharge_port_id':rec.dis_port_id.id,'load_port_id':rec.load_port_id.id})
				op_rec_new_context.write({'shipping_line_id':rec.shipping_line_id.id})
				op_rec_new_context.write({'vessel_id':rec.vessel_id.id})
				op_rec_new_context.voyage_no = rec.voyage_no
				for pre in precar_rec:
					pre.dis_port_id = rec.load_port_id
					pre.shipping_line_id = rec.shipping_line_id
					pre.vessel_id = rec.vessel_id
					pre.voyage_no = rec.voyage_no
				for on in oncar_rec:	
					on.load_port_id = rec.dis_port_id
					on.shipping_line_id = rec.shipping_line_id
					on.vessel_id = rec.vessel_id
					on.voyage_no = rec.voyage_no							
		return write_returned