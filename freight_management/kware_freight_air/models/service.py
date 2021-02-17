from odoo import models, fields, api,exceptions
from odoo.tools.translate import _

class ServiceInherit(models.Model):
	_inherit = 'frg.service'


	@api.onchange('main')
	def _get_vendor(self):
		if self.main :
			if self.routing_id.trans_mode == 'land':
				self.vendor_id = self.routing_id.trucker_id
			elif self.routing_id.trans_mode == 'ocean':
				self.vendor_id = self.routing_id.shipping_line_id
			elif self.routing_id.trans_mode == 'air':
				self.vendor_id = self.routing_id.airline_id