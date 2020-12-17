# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# License URL :<https://store.webkul.com/license.html/>
##########################################################################

from odoo import api, http, fields, models, _
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta
import datetime, pytz
import base64
import traceback

import logging
_logger = logging.getLogger(__name__)

Days = {
    0 : 'mon',
    1 : 'tue',
    2 : 'wed',
    3 : 'thu',
    4 : 'fri',
    5 : 'sat',
    6 : 'sun',
}
class Website(models.Model):
    _inherit = 'website'

    @api.model
    def bk_products_validation(self):
        """"Check any sold out product of booking type is in the cart or not."""
        order = self.sale_get_order()
        if order:
            order_lines = order.website_order_line
            for line in order_lines:
                product_obj = line.product_id.product_tmpl_id
                if product_obj.is_booking_type:
                    av_qty = product_obj.get_bk_slot_available_qty(line.booking_date, line.booking_slot_id.id)
                    if av_qty < 0:
                        break
            else:
                return True
        return False

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_booking_type = fields.Boolean(string="Booking Order")
    payment_start_date = fields.Datetime("Payment initiated time")

    @api.model
    def create(self, vals):
        seq = 0 
        if vals.get('order_line'):
            for line in vals.get('order_line'):
                l = line[2]
                l['sequence'] = seq
                seq+=1

        return super(SaleOrder, self).create(vals)
    # def _create_payment_transaction(self, vals):
    #     res = super(SaleOrder, self)._create_payment_transaction(vals)
    #     for so in self:
    #         for line in so.order_line:
    #             seats = self.env['seat.book'].sudo().search([('sale_line_id','=',line.id)])
    #             seats.book_paid = True

    #     return res
    def check_active_bk_transactions(self):
        self.ensure_one()
        active_trans = self.transaction_ids.filtered(lambda l: l.state in ['pending', 'authorized', 'done'])
        if active_trans:
            return True
        return False

    @api.onchange('order_line')
    def compute_booking_type(self):
        for rec in self:
            if rec.order_line:
                if any(line.product_id.is_booking_type == True for line in rec.order_line):
                    rec.is_booking_type = True
                    return
                for l in rec.order_line:
                    if l.product_id.is_combo:
                        for p in l.product_id.pos_combo_item_ids:
                                if p.product_id.is_booking_type:
                                    rec.is_booking_type = True 
    
    
    def is_attraction(self):
        for rec in self:
            if rec.order_line:
                if any(line.product_id.is_booking_type == True for line in rec.order_line) or any(line.product_id.categ_id.attraction_ticket == True for line in rec.order_line):
                    return True
                for l in rec.order_line:
                    if l.product_id.is_combo:
                        for p in l.product_id.pos_combo_item_ids:
                                if p.product_id.is_booking_type or p.product_id.categ_id.attraction_ticket:
                                    return True 
        return False

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        if line_id:
            order_line = self.env['sale.order.line'].sudo().browse(line_id)
            if order_line.product_id.is_combo:
                last_qty = order_line.product_uom_qty
                if set_qty:
                    quantity = set_qty
                elif add_qty is not None:
                    quantity = order_line.product_uom_qty + (add_qty or 0)
                else:
                    quantity = 0
                if quantity < last_qty:
                    book_datas = self.env['seat.book'].sudo().search([('sale_line_id','=',line_id)])
                    if book_datas:
                        seats = book_datas.sudo()
                        for s in seats:
                            if 'payment' not in s.name:
                                s.name = s.name+'_no_payment'
        res = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
    
        return res

    @api.model
    def remove_product_cart(self):
        sale_order = self.search([('state','=','draft'),('website_id', '!=', False)])
        params = self.env['ir.config_parameter'].sudo()
        for so in sale_order:
            if not so.check_so_is_membership():
                rd = relativedelta(datetime.datetime.now(), so.write_date)
                if rd.minutes > int(params.get_param('max_time_for_shopping')):
                    if not so.transaction_ids:
                        for order_line in so.order_line:
                            if order_line.redeem_loyalty:
                                membership_history = self.env['membership.history'].sudo().search([('sale_line_id','=',order_line.id)])
                                for history in membership_history:
                                    history.unlink()
                            if order_line.order_id.is_booking_type:
                                seat_book = self.env['seat.book'].sudo().search([('sale_line_id','=',order_line.id)])
                                for seat in seat_book:
                                    if 'cart_timeout' not in seat.name:
                                        seat.name = seat.name+'_cart_timeout'
                                    # seat.unlink()
                        so.action_cancel()
                        # so.unlink();


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    booked_slot_id = fields.Many2one(related="booking_slot_id.time_slot_id", string="Booked Slot", store=True)
    booked_plan_id = fields.Many2one(related="booking_slot_id.plan_id", string="Booked Plan", store=True)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    booking_slot_id = fields.Many2one("booking.slot", string="Booking Slot")
    booking_date = fields.Date(string="Booking Date")
    seat_number = fields.Char()
    seat_barcodes = fields.Char()
    booked_slot_id = fields.Many2one(related="booking_slot_id.time_slot_id", string="Booked Slot", store=True)
    booked_plan_id = fields.Many2one(related="booking_slot_id.plan_id", string="Booked Plan", store=True)

   
    def max_seat(self, combo):
        
        max_qty = combo.quantity * self.product_uom_qty
        book_seat = self.env['seat.book'].sudo().search([('sale_line_id','=', self.id),('product_id','=',combo.product_id.id)])
        if len(book_seat) == max_qty:
            return True
        return False

    def get_seat_data(self, combo=False):
        seats = []
        if combo:
            book_seat = self.env['seat.book'].sudo().search([('sale_line_id','=', self.id),('product_id','=',combo.product_id.id)])
            for b in book_seat:
                seats.append(b.name)
            
        else:
            book_seat = self.env['seat.book'].sudo().search([('sale_line_id','=', self.id)])
            for b in book_seat:
                seats.append(b.name)

        return ', '.join(seats)

    @api.depends('product_id','booking_date','booking_slot_id')
    def compute_booking_line_name(self):
        for rec in self:
            if rec.product_id.is_booking_type:
                rec.name = ''
                product_obj = rec.product_id or False
                if product_obj and product_obj.is_booking_type:
                    name = "Booking for " + product_obj.name
                    if rec.booking_date:
                        name += " on " + str(rec.booking_date)
                    if rec.booking_slot_id:
                        if len(rec.booking_slot_id.name_get()) > 0:
                            name += " (" + rec.booking_slot_id.name_get()[0][1] + ")"
                    rec.name = name
        return

    @api.model
    def create(self, vals):
        _logger.info("~~~1~~~~~create~~~~~~~~~~~%r~~~~~~~~~~~~",vals)
        res = super(SaleOrderLine, self).create(vals)
        res.compute_booking_line_name()
        return res

    def write(self, vals):
        _logger.info("~~~1~~~~~booking_date~~~~~~~~~~~%r~~~~~~~~~~~~",vals)
        res = super(SaleOrderLine, self).write(vals)
        _logger.info("~~~~2~~~~booking_date~~~~~~~~~~~%r~~~~~~~~~~~~",vals.get('booking_date'))
        if vals.get('booking_date') or vals.get('booking_slot_id') or vals.get('product_id'):
            self.compute_booking_line_name()
        return res

    @api.onchange('product_id','booking_date','booking_slot_id')
    def booking_values_change(self):
        for rec in self:
            rec.compute_booking_line_name()
        return

    # def _get_display_price(self, product):
    #     for rec in self:
    #         if rec.booking_slot_id:
    #             return rec.booking_slot_id.with_context(pricelist=self.order_id.pricelist_id.id).price
    #     return super(SaleOrderLine, self)._get_display_price(product)

    @api.model
    def remove_booking_product_draft_order_lines(self):
        bk_orders = self.search([('state','=','draft'),('booking_slot_id','!=',None)])
        for so in bk_orders:
            sale_order = so.order_id
            payment_start_date = sale_order.payment_start_date
            rd = relativedelta(datetime.datetime.now(), so.create_date)
            if not payment_start_date:
                if rd.minutes > 5:
                    so.action_cancel()
            else:
                prd = relativedelta(datetime.datetime.now(), payment_start_date)
                if prd.minutes > 10:
                    if not sale_order.check_active_bk_transactions():
                        so.action_cancel()
                        sale_order.compute_booking_type()
                        if not sale_order.is_booking_type:
                            sale_order.payment_start_date = None

            

    

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_booking_type = fields.Boolean("Available for booking")
    br_start_date = fields.Date("Start Date")
    br_end_date = fields.Date("End Date")
    blocked_date = fields.Date("Blocked Date")
    max_bk_qty = fields.Integer("Max Booking Qty")
    booking_day_slot_ids = fields.One2many("day.slot.config", "product_id", string="Configure Day Slots")
    trailer = fields.Binary(string="Trailer")
    trailer_attachment = fields.Many2one('ir.attachment')
    file_name = fields.Char()

    def get_base_url(self):
        website = self.env['website'].sudo().search([],limit=1)
        base_url = website.domain
        return base_url+'/'

    def get_available_bk_qty(self):
        for rec in self:
            context = dict(rec._context) or {}
            context['active_id'] = rec.id
            return {
                'name':'Booking Available Quantity',
                'type':'ir.actions.act_window',
                'res_model':'booking.quantity.wizard',
                'view_mode':'form',
                # 'view_type':'form',
                'view_id':rec.env.ref('movie_booking_system.booking_available_quantity_wizard_form_view').id,
                'context' : context,
                'target':'new',
            }

    @api.model
    def get_bk_slot_available_qty(self, bk_date, slot_plan_id):
        """ Return: Total quantity available on a particular date in a provided slot.
            bk_date: Date on with quantity will be calculated.
            slot_plan_id: Plan in any slot on with quantity will be calculated."""
        slot_plan_obj = self.env["booking.slot"].browse([int(slot_plan_id)])
        sol_objs = slot_plan_obj.line_ids.filtered(lambda line: line.booking_date == bk_date).mapped('product_uom_qty')
        return slot_plan_obj.quantity - sum(sol_objs)

    def get_bk_open_closed_days(self, state):
        """State : State of the booking product(open/closed).
            Return: List of days of the week on the basis of state.
            e.g.-['mon','tue','sun']"""
        bk_open_days = self.booking_day_slot_ids.filtered(lambda day_sl: day_sl.booking_status == 'open' and len(day_sl.booking_slots_ids)).mapped('name')
        if state == 'open':
            return bk_open_days
        else:
            bk_closed_days = list(set(Days.values()) - set(bk_open_days))
            return bk_closed_days

    @api.model
    def get_available_day_slots(self, slots, sel_date):
        av_slots = []
        if sel_date and slots:
            rd = relativedelta(datetime.date.today(), sel_date)
            if rd.days == 0 and rd.months == 0 and rd.years == 0:
                for slot in slots:
                    start_time = slot.start_time
                    start_time = slot.float_convert_in_time(start_time)
                    
                    user_id = self.env['res.users'].sudo().browse(1).tz
                    current_time = datetime.datetime.now().replace(microsecond=0).replace(second=0)
                    user_tz = pytz.timezone(user_id)
                    current_time = pytz.utc.localize(current_time).astimezone(user_tz)
                    print("====current time ====",current_time)
                    hour = int(start_time.split(":")[0])
                    min = int(start_time.split(":")[1])
                    if hour > current_time.hour or (hour == current_time.hour and min > current_time.minute):
                        av_slots.append(slot)
                return av_slots
        return slots

    def get_booking_slot_for_day(self, sel_date):
        """Return: List of slots and their plans with qty and price of a day"""
        self.ensure_one()
        day = Days[sel_date.weekday()]
        day_config = self.booking_day_slot_ids.filtered(lambda day_sl: day_sl.name == day and day_sl.booking_status == 'open')
        day_slots = day_config.booking_slots_ids.sorted(key=lambda r: r.time_slot_id.start_time)
        time_slots = day_slots.mapped('time_slot_id')
        time_slots = self.get_available_day_slots(time_slots, sel_date)
        slots_plans_list = []
        for slot in time_slots:
            d1 = {}
            d2 = []
            d1['slot'] = {
                'name' : slot.name_get()[0][1],
                'id' : slot.id,
                'start_time' : slot.float_convert_in_time(slot.start_time),
            }
            d_slots = day_slots.filtered(lambda r: r.time_slot_id.id == slot.id)
            for d in d_slots:
                d2.append({
                    'name' : d.plan_id.name,
                    'id' : d.id,
                    'qty' : d.quantity,
                    'price' : d.price,
                })
            d1['plans'] = d2
            slots_plans_list.append(d1)
        return slots_plans_list

    def get_booking_onwards_price(self):
        """Return: Minimum price of a booking product available in any slot."""
        self.ensure_one()
        prices = sorted(self.booking_day_slot_ids.mapped('booking_slots_ids.price'))
        return prices[0] if prices else 0

    @api.onchange('br_start_date')
    def booking_start_date_validation(self):
        self.validate_booking_dates(start_date=self.br_start_date)

    @api.onchange('br_end_date')
    def booking_end_date_validation(self):
        self.validate_booking_dates(end_date=self.br_end_date)

    @api.onchange('is_booking_type')
    def update_product_type_for_booking(self):
        if self.is_booking_type:
            self.type = 'service'

    def validate_booking_dates(self, start_date=None, end_date=None):
        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        current_date = fields.Date.today()
        if start_date and end_date:
            if start_date < current_date:
                raise UserError(_("Please enter start date correctly. Start date should't be smaller then the current date."))
            if end_date < start_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the start date."))
            return True
        if start_date:
            if start_date < current_date:
                raise UserError(_("Please enter start date correctly. Start date should't be smaller then the current date."))
            if self.br_end_date and start_date > self.br_end_date:
                raise UserError(_("Please enter start date correctly. Start date should't be greater then the end date."))
            return True
        if end_date:
            if end_date < current_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the current date."))
            if self.br_start_date and end_date < self.br_start_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the start date."))
            return True

    @api.model
    def create(self, vals):
        self.validate_booking_dates(vals.get("br_start_date"), vals.get("br_end_date"))
        res = super(ProductTemplate, self).create(vals)
        if vals.get('trailer'):
            attachment_id = self.env['ir.attachment'].sudo().create({
                'name': res.name+'_'+res.file_name,
                'datas': vals.get('trailer'),
                'res_id': res.id,
                'type': 'binary',
                'res_model': 'product.template',
                'res_field': 'Trailer',
                'public': True
            })
            res.trailer_attachment = attachment_id.id
        return res

    def write(self, vals):
        for rec in self:
            old_attachment = rec.trailer_attachment
            
            if vals.get('trailer'):
                attachment_id = self.env['ir.attachment'].sudo().create({
                    'name': rec.name+'_'+vals.get('file_name'),
                    'type': 'binary',
                    'datas': vals.get('trailer'),
                    'res_id': rec.id,
                    'res_model': 'product.template',
                    'res_field': 'Trailer',
                    'public': True
                }) 
                vals['trailer_attachment'] = attachment_id.id 
                if old_attachment:
                    old_attachment.unlink()
            rec.validate_booking_dates(vals.get("br_start_date"), vals.get("br_end_date"))
        return super(ProductTemplate, self).write(vals)
