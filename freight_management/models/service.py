from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class Service(models.Model):
	_name = 'frg.service'

	product_id = fields.Many2one('product.product',string='Service ',required=True,index=True,domain=[('type','=','service')],context={'default_type':'service'})
	name = fields.Char(string='Description',required=True)
	operation_id = fields.Many2one('frg.operation',string='Operation ',required=True)
	cost = fields.Float(string='Cost ',digits=(16, 2),store=True)
	sale = fields.Float(string='Sale ',digits=(16,2),store=True)
	curr_id = fields.Many2one('res.currency',string="Currency",required=True)
	routing_id = fields.Many2one('frg.carraige',string='Route',required=True)
	vendor_id = fields.Many2one('res.partner',string='Vendor',required=True)
	main = fields.Boolean(string='Main',default=False)
	lump_sum = fields.Boolean(string="Lump Sum",default=False)
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
	shippment_type = fields.Selection( required=True, string='Shippment Type', selection=[(u'FCL', u'FCL'), (u'LCL', u'LCL')],default='FCL',related='operation_id.shippment_type')

	payable_ids = fields.Many2many('freight.payable', 'frg_service_freight_payable_rel', 'freight_service_id', 'freight_payable_id', 
		string='Payables'
	)
	
	receivable_ids = fields.Many2many('freight.receivable', 'frg_service_freight_receivable_rel', 'frg_service_id', 'freight_receivable_id',
		string='Receivables',
	)


	@api.onchange('product_id')
	def _get_cost(self):
		self.cost=self.product_id.standard_price
		self.sale=self.product_id.list_price




	@api.onchange('main')
	def _get_vendor(self):
		if self.main :
			if self.routing_id.trans_mode == 'land':
				self.vendor_id = self.routing_id.trucker_id
			elif self.routing_id.trans_mode == 'ocean':
				self.vendor_id = self.routing_id.shipping_line_id

