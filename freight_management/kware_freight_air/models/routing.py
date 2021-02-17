from odoo import models, fields, api,exceptions
from odoo.tools.translate import _
from odoo.addons.freight_management.models.routings import FrgCarraige

class FrgCarraigeInherit(FrgCarraige):

	def write(self,vals):
		write_returned = super(FrgCarraige,self).write(vals)
		copied_context = self._context.copy()
		copied_context.update({'test':True})
		for rec in self:
			precar_rec = rec.search([('rtype','=','precar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			oncar_rec  = rec.search([('rtype','=','oncar'),('frg_operation_id','=',rec.frg_operation_id.id)])
			if rec.rtype == 'main':
				op_rec = self.env['frg.operation'].browse(rec.frg_operation_id.id)
				op_rec_new_context = op_rec.with_context(copied_context)
				op_rec_new_context.write({'discharge_port_id':rec.dis_port_id.id,'load_port_id':rec.load_port_id.id})
				op_rec_new_context.write({'shipping_line_id':rec.shipping_line_id.id})
				op_rec_new_context.write({'vessel_id':rec.vessel_id.id})
				op_rec_new_context.write({'airline_id':rec.airline_id.id})
				op_rec_new_context.write({'flight_no':rec.flight_no})
				op_rec_new_context.write({'tracking_no':rec.tracking_no})
				op_rec_new_context.voyage_no = rec.voyage_no
				for pre in precar_rec:
					pre.dis_port_id = rec.load_port_id
					pre.shipping_line_id = rec.shipping_line_id
					pre.vessel_id = rec.vessel_id
					pre.airline_id = rec.airline_id
					pre.flight_no = rec.flight_no
					pre.tracking_no = rec.tracking_no
				for on in oncar_rec:	
					on.load_port_id = rec.dis_port_id
					on.shipping_line_id = rec.shipping_line_id
					on.vessel_id = rec.vessel_id
					on.voyage_no = rec.voyage_no							
					on.airline_id = rec.airline_id							
					on.flight_no = rec.flight_no							
					on.tracking_no = rec.tracking_no												
		return write_returned


class FrgCarraige_2(models.Model):
    _inherit = 'frg.carraige'

    def _get_loading_port_label(self):
        for obj in self:
            val = "gateway"
            if obj.trans_mode and obj.trans_mode != 'air':
                val = "loading_port"
            obj.load_port_lable = val

    def _get_discharge_port_label(self):
        for obj in self:
            val = "destination"
            if obj.trans_mode and obj.trans_mode != 'air':
                val = 'discharge_port'
            obj.discharge_port_label = val

    trans_mode = fields.Selection( required=True, string='Trans Mode', selection=[(u'ocean', u'Ocean'), (u'land', u'Inland'),(u'air',u'Air')])

    airline_id = fields.Many2one('res.partner',string='Airline',ondelete='restrict',domain=[('airline','=',True)],context={"default_airline":True})
    flight_no  = fields.Char( size=128, string='Flight No')
    tracking_no = fields.Char(size=128, string='Tracking No')
    load_port_lable = fields.Selection([('gateway', 'Gateway'), ('loading_port', "Loading Port")],
                                       compute="_get_loading_port_label")
    discharge_port_label = fields.Selection([('destination', 'Destination'), ('discharge_port', 'Discharge Port')],
                                            compute="_get_discharge_port_label")

