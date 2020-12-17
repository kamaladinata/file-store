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

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import traceback
import math
import pytz
from datetime import datetime, date
import logging
_logger = logging.getLogger(__name__)

Days = [
    ('sun','Sunday'),
    ('mon','Monday'),
    ('tue','Tuesday'),
    ('wed','Wednesday'),
    ('thu','Thursday'),
    ('fri','Friday'),
    ('sat','Saturday'),
]

Days_for_change = {
    0 : 'mon',
    1 : 'tue',
    2 : 'wed',
    3 : 'thu',
    4 : 'fri',
    5 : 'sat',
    6 : 'sun',
}

Days_dict= {
    'sun':'Sunday',
    'mon':'Monday',
    'tue':'Tuesday',
    'wed':'Wednesday',
    'thu':'Thursday',
    'fri':'Friday',
    'sat':'Saturday',
}


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    max_booking_in_advance = fields.Integer('Maximum Booking in Advance',default=7)
    payment_expired = fields.Integer('Payment Expired in (Days)',default=7)
    ecom_source = fields.Char('barcode ecommerce prefix',default='ECOM')
    max_time_for_shopping= fields.Integer('Maximum Time to Shopping',default=1)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'max_booking_in_advance': int(params.get_param('max_booking_in_advance')),
            'payment_expired': int(params.get_param('payment_expired')),
            'ecom_source': params.get_param('ecom_source'),
            'max_time_for_shopping': int(params.get_param('max_time_for_shopping')),
            })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('max_booking_in_advance', self.max_booking_in_advance)
        params.set_param('ecom_source', self.ecom_source)
        params.set_param('payment_expired', self.payment_expired)
        params.set_param('max_time_for_shopping', self.max_time_for_shopping)


class BookingPlan(models.Model):
    _name = "booking.plan"

    name = fields.Char(string="Name", required=True)
    discription = fields.Html(string="Description", help="Booking plan description.")
    sequence = fields.Integer(help="Determine the display order", default=1)

    def _check_unique_insesitive(self, context=None):
        recs = self.search_count([('name', '=ilike', self.name)])
        if recs > 1:
            return False
        return True

    _constraints = [(_check_unique_insesitive, _('This booking plan is already exist!'), ['name'])]

class BookingTimeSlot(models.Model):
    _name = "booking.time.slot"

    sequence = fields.Integer(help="Determine the display order", default=1)
    start_time = fields.Float(string="Start Time", required=True, help="Enter slot start time.")
    end_time = fields.Float(string="End Time", required=True, help="Enter slot end time.")

    # SQL Constraints
    _sql_constraints = [
        ('booking_time_slot_uniq', 'unique(start_time, end_time)', _('This time slot is already exist.'))
    ]

    def float_convert_in_time(self, float_val):
        """Convert any float value in 24 hrs time formate."""
        if float_val < 0:
            float_val = abs(float_val)
        hour = math.floor(float_val)
        min = round((float_val % 1) * 60)
        if min == 60:
            min = 0
            hour = hour + 1
        time = str(hour).zfill(2) + ":" + str(min).zfill(2)
        return time

    def time_convert_in_float(self, time_val):
        """Convert any 24 hrs time fomate value in float."""
        factor = 1;
        if time_val[0] == '-':
            time_val = time_val[1:]
            factor = -1
        float_time_pair = time_val.split(":")
        if len(float_time_pair) != 2:
            return factor*float(time_val)
        hours = int(float_time_pair[0])
        minutes = int(float_time_pair[1])
        return factor * round((hours + (minutes / 60)),2)

    def name_get(self):
        """Return: [(id, start_time-end_time)],
            e.g-[(1, 1:00-3:00)]"""
        result = []
        for rec in self:
            name = self.float_convert_in_time(rec.start_time) + '-' + self.float_convert_in_time(rec.end_time)
            result.append((rec.id, name))
        return result

    def check_time_values(self, vals):
        start_time = vals.get('start_time') if vals.get('start_time', None) != None else self.start_time
        end_time = vals.get('end_time') if vals.get('end_time', None) != None else self.end_time
        if start_time >= 24 or start_time < 0:
            raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))
        if end_time >= 24 or end_time < 0:
            raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))
        if start_time >= end_time:
            raise UserError(_("Please enter a valid start and end time."))
        same_objs = self.search([('start_time','=',start_time),('end_time','=',end_time)])
        if len(same_objs.ids) > 0:
            raise UserError(_("Record already exist with same timing."))

    @api.model
    def create(self, vals):
        self.check_time_values(vals)
        res = super(BookingTimeSlot, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('start_time', None) != None and vals.get('end_time', None) != None:
            self.check_time_values(vals)
        elif vals.get('start_time', None) != None or vals.get('end_time', None) != None:
            for rec in self:
                rec.check_time_values(vals)
        res = super(BookingTimeSlot, self).write(vals)
        return res

class BookingSlotConfig(models.Model):
    _name = "day.slot.config"

    @api.onchange('name')
    def _day_string(self):
        for i in self:
            if i.name:
                i.day = Days_dict[i.name]

    name = fields.Selection(selection=Days, string="Day", required=True)

    ticket_name = fields.Char(related="product_id.name")
    day = fields.Char('Day', compute="_day_string", Store=True)
    booking_status = fields.Selection(selection=[('open','Open'),('closed','Closed')], string="Status(Closed/Open)", required=True, help="Select booking status for the day(Closed/Open).", default="open")
    booking_slots_ids = fields.One2many("booking.slot", "slot_config_id", string="Booking Slots", help="Add booking slots for the day.")
    product_id = fields.Many2one("product.template", string="Product")

    # SQL Constraints
    _sql_constraints = [
        ('booking_day_uniq', 'unique(name, product_id)', _("Record already exist, you can't create multiple records for the same day."))
    ]

    @api.onchange('booking_slots_ids')
    def validate_slot_plan(self):
        if self.booking_slots_ids:
            saved_data = self.env["booking.slot"].browse(self.booking_slots_ids.ids);
            new_data = self.booking_slots_ids - saved_data
            for rec in new_data:
                if rec.time_slot_id and rec.plan_id:
                    x = saved_data.filtered(lambda l: l.time_slot_id == rec.time_slot_id and l.plan_id == rec.plan_id)
                    if len(x) > 0:
                        raise UserError(_("Record already exist with same time slot and plan."))


class BookingSlot(models.Model):
    _name = "booking.slot"

    time_slot_id = fields.Many2one("booking.time.slot", required=True, string="Time Slot")
    start_time = fields.Float(string="Start Time", related="time_slot_id.start_time")
    end_time = fields.Float(string="End Time", related="time_slot_id.end_time")
    plan_id = fields.Many2one("booking.plan", required=False, string="Booking Plan")
    quantity = fields.Integer(string="Quantity")
    price = fields.Float(string="Price", required=True)
    slot_config_id = fields.Many2one("day.slot.config", string="Day Slot Config")
    line_ids = fields.One2many("sale.order.line", "booking_slot_id", string="Ecommerce Booking Orders")
    pos_line_ids = fields.One2many("pos.order.line", "booking_slot_id", string="POS Booking Orders")
    is_today = fields.Boolean(compute="compute_today_show", search='_value_search')
    ticket_name = fields.Char(related="slot_config_id.product_id.name")
    day = fields.Char(related="slot_config_id.day")

    

    def action_open_scanning(self):
        
        return {
            'type': 'ir.actions.client',
            'tag': 'scan_ticket_main_menu',
            'target': 'fullscreen',
            'context': {'time_slot_id': self.time_slot_id.id,
                'day': self.day,
                'start_time': self.start_time,
                'ticket_name': self.ticket_name,
                'end_time': self.end_time
            },
            
        }
    
    def compute_today_show(self):
        for slot in self:
            if not slot.slot_config_id.product_id.active:
                slot.update({
                    'is_today': False
                })
                continue
            today = datetime.today().strftime('%a').lower()
            prod = slot.slot_config_id.product_id
            start_date = False
            end_date = False
            if not prod.br_start_date or not prod.br_end_date:
                slot.update({
                    'is_today': False
                })
                continue
            start_date = datetime.strptime(str(prod.br_start_date),'%Y-%m-%d').date()
            end_date = datetime.strptime(str(prod.br_end_date),'%Y-%m-%d').date()
            today_date = datetime.today().date()
            if slot.slot_config_id.name in today and (today_date >= start_date and today_date <= end_date):
                slot.update({
                    'is_today': True
                })
            else:
                slot.update({
                    'is_today': False
                })

    def _value_search(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.is_today is True )
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        else:
            # means no show today, so make domain that imposible
            return [('id','=','0')]

    def name_get(self):
        result = []
        for rec in self:
            print("time slot id ==========",rec.time_slot_id.name_get())
            if len(rec.time_slot_id.name_get()) > 0:
                name = rec.time_slot_id.name_get()[0][1]
                result.append((rec.id, name))
        return result

    def _check_unique_slot_plan(self, context=None):
        for rec in self:
            recs = self.search_count([('time_slot_id', '=', rec.time_slot_id.id), ('plan_id', '=', rec.plan_id.id), ('slot_config_id', '=', rec.slot_config_id.id)])
            if recs > 1:
                return False
            return True

    _constraints = [(_check_unique_slot_plan, _('This booking slot is already exist.'), ['time_slot_id', 'plan_id', 'slot_config_id'])]

class BookingConfig(models.Model):
    _name = "booking.config"

    day = fields.Selection(selection=Days, string="Day")
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    time_slot = fields.Integer("Slot time duration")
    buffer_cache = fields.Integer("Buffer cache time after each booking")
    br_start_time = fields.Float("Break Start Time")
    br_end_time = fields.Float("Break End Time")
    product__id = fields.Many2one("product.template", string="Bookng Product")

class SeatBooking(models.Model):
    _name = 'seat.book'

    name = fields.Char('Seat Name', required=1)
    booking_slot_id = fields.Many2one("booking.slot", string="Booking Slot")
    booking_date = fields.Date(string="Booking Date")
    user_id = fields.Many2one('res.users','Booked User')
    pos_line_id = fields.Many2one('pos.order.line', 'POS Order Line')
    sale_line_id = fields.Many2one('sale.order.line', 'Web Order Line')
    order_reference = fields.Char('Order Reference', compute="_get_order_reference",store=True)
    book_paid = fields.Boolean('Paid ?')
    attended = fields.Boolean('Attended ?')
    product_id = fields.Many2one('product.template')
    product_order = fields.Many2one('product.product',compute="_get_product_by_order",store=True)
    barcode_order = fields.Char()
    ip_client = fields.Char('User Session')
    pos_line = fields.Char()

    @api.onchange('booking_date','product_id')
    def update_bk_slots_domain(self):
        bk_product = self.product_id
        if bk_product and self.booking_date:
            slot_plan_ids = []
            start_date = datetime.strptime(str(bk_product.br_start_date),'%Y-%m-%d').date()
            end_date = datetime.strptime(str(bk_product.br_end_date),'%Y-%m-%d').date()
            bk_date = datetime.strptime(str(self.booking_date),'%Y-%m-%d').date()
            if bk_date < start_date or bk_date > end_date:
                raise UserError(_("Selected Date is beyond the configured start and end date."))
            if start_date <= bk_date and bk_date <= end_date:
                bk_day = Days_for_change[bk_date.weekday()]
                slot_plan_objs = bk_product.booking_day_slot_ids.filtered(lambda day_sl: day_sl.name == bk_day and day_sl.booking_status == 'open').mapped('booking_slots_ids')
                slot_plan_ids = slot_plan_objs.ids if slot_plan_objs else slot_plan_ids
            domain = [('id', 'in', slot_plan_ids)]
            self.booking_slot_id = None
            return {'domain': {'booking_slot_id': domain }}

    def unbook_no_payment(self, duration):
        unbook = self.env['seat.book'].search([('book_paid','=',False)])
        for s in unbook:
            if s.name and ('no_payment' not in s.name and 'cart_timeout' not in s.name):
                now = fields.Datetime.now()
                create_date = s.write_date
                dif = now - create_date
                minutes = dif.seconds / 60
                if minutes > duration:
                    if s.order_reference:
                        so = self.env['sale.order'].search([('name','=', s.order_reference)])
                        if so and so.amount_total > 0:
                            s.name = s.name+'_no_payment'
                            so.action_cancel()
                    else:
                        s.name = s.name+'_no_payment'
            else:
                continue

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Ticket - %s' % (self.name)

    def get_review_link(self):
        review_link = self.env['ir.config_parameter'].sudo().get_param('social.media.link', '')
        if review_link:
            return review_link
        else:
            return False

    def convert_int(self,float):
        return int(float)

    def uppercase(self,char):
        return char.upper()

    def _get_current_date(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _get_sgd_current_date(self):
        kuala_lumpur=pytz.timezone('Asia/Kuala_Lumpur')
        now_in_kuala_lumpur=datetime.now().astimezone(kuala_lumpur)
        return now_in_kuala_lumpur.strftime("%d/%m/%Y %H:%M:%S")

    @api.depends('pos_line_id','sale_line_id')
    def _get_product_by_order(self):
        for line in self:
            if line.pos_line_id:
                line.product_order = line.pos_line_id.product_id.id
            elif line.sale_line_id:
                line.product_order = line.sale_line_id.product_id.id
            else:
                line.product_order = False

    @api.depends('pos_line_id','sale_line_id','pos_line_id.order_id.name')
    def _get_order_reference(self):
        for line in self:
            if line.pos_line_id:
                line.order_reference = line.pos_line_id.order_id.name
            elif line.sale_line_id:
                line.order_reference = line.sale_line_id.order_id.name
            else:
                line.order_reference = False
             
    # @api.depends('pos_line_id','sale_line_id')
    # def get_barcode_order(self):
    #     for line in self:
    #         if line.pos_line_id and line.pos_line_id.barcode_order:
    #             line.barcode = line.pos_line_id.barcode_order
    #         else:
    #             line.barcode = False
    @api.model
    def unbook_combo(self, lines):
        lines = self.env['pos.order.line'].browse(lines)
        for l in lines:
            for booking_data in l.booking_slot_line_ids:
                if booking_data.seat_number and booking_data.booking_slot_id.id and booking_data.booking_date:
                    seat_list = booking_data.seat_number.strip('][').replace("'", "").split(',')
                    seats_unbook = self.env['seat.book'].search([('name','in',seat_list),('booking_date','=',booking_data.booking_date),('booking_slot_id','=',booking_data.booking_slot_id.id)])
                    for s in seats_unbook:
                        s.name = s.name+'_no_payment'
                    # seats_unbook.unlink()

       

    @api.model
    def clean_booking_data(self):
        today = date.today()
        old_book = self.env['seat.book'].search([('booking_date','<',today)])
        # old_book.unlink()

    
    @api.model
    def check_attendance(self):
        company_user = self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            default_location_id = warehouse.lot_stock_id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name,))

        action = self.env.ref('stock_barcode.stock_barcode_inventory_client_action').read()[0]
        if self.env.ref('stock.warehouse0', raise_if_not_found=False):
            new_inv = self.env['stock.inventory'].create({
                'start_empty': True,
                'name': fields.Date.context_today(self),
                'location_ids': [(4, default_location_id.id, None)],
            })
            new_inv.action_start()
            action['res_id'] = new_inv.id

            params = {
                'model': 'stock.inventory',
                'inventory_id': new_inv.id,
            }
            action['context'] = {'active_id': new_inv.id}
            action = dict(action, target='fullscreen', params=params)

        return action

    def get_set_running_number(self):
        config = self.env['res.config.settings'].sudo()
        running_number = config.get_sequence_order()+1
        config.set_sequence_order(running_number)
        return running_number

    @api.model
    def unbook_seats(self, seats):
        seat_obj = self.env['seat.book'].sudo()
        for seat in seats:
            if not seat:
                continue
            seatdata = seat_obj.search([('booking_date','=', seat.get('booking_date')) ,('name','in',seat.get('seat_ids')), ('booking_slot_id','=',seat.get('booking_slot_id'))])
            if seatdata:
                for s in seatdata:
                    if 'payment' not in s.name:
                        s.name = s.name+'_no_payment'
                # seatdata.unlink()
        return seats


    @api.model
    def togglebook(self, seat):
        if not seat:
            return
        seat_obj = self.env['seat.book'].sudo()
        seats = []
        prod = self.env['product.template'].sudo().browse(seat.get('product_id'))
        activity_type = prod.categ_id.activity_type or ''
        date = datetime.today().strftime('%y%m%d') or ''
        
        seatdata = seat_obj.search([('booking_date','=', seat.get('booking_date')) ,('name','=',seat.get('seat_id')), ('booking_slot_id','=',seat.get('booking_slot_id'))],limit=1)
        if not seatdata and seat.get('book'):
            seat_new = seat_obj.create({
                'name': seat.get('seat_id'),
                'booking_date': seat.get('booking_date'),
                'booking_slot_id': seat.get('booking_slot_id'),
                'product_id': seat.get('product_id'),
                'barcode_order': seat.get('barcode'),
                'user_id': seat.get('user_id'),
                'pos_line': seat.get('order_reference')
            })
            s = {
                'name': seat_new.name,
                'barcode_order': seat_new.barcode_order,
                'book': True
            }
            seats.append(s)
            print("seastsss wiht barcode ------",seats)
        if seatdata and not seat.get('book'):
            for seat_book in seatdata:
                seats.append({
                    'name': seat_book.name,
                    'barcode_order': seat_book.barcode_order,
                    'book': False
                })
            for s in seatdata.sudo():
                if 'payment' not in s.name:
                    s.name = s.name+'_no_payment'
            # seatdata.sudo().unlink()
        
        return seats

    @api.model
    def unbook(self, seats):
        seat_obj = self.env['seat.book'].sudo()
        for seat in seats:
            seatdata = seat_obj.search([('booking_date','=', seat.get('booking_date')) ,('name','in',seat.get('seat_ids')), ('booking_slot_id','=',seat.get('booking_slot_id'))])
            # seatdata.unlink()
            for s in seatdata:
                if 'payment' not in s.name:
                    s.name = s.name+'_no_payment'
        return seats

    @api.model
    def cleannotpaid(self, seat):
        seat_obj = self.env['seat.book'].sudo()
        seatdata = seat_obj.search([('book_paid','=', False), ('sale_line_id','=',seat.get('line_id')), ('user_id','=',seat.get('user_id')), ('product_id','=',seat.get('product_id'))])
        if not seat.get('user_id'):
            seatdata = seat_obj.search([('book_paid','=', False), ('sale_line_id','=',seat.get('line_id')),('ip_client','=',seat.get('ip_client')), ('product_id','=',seat.get('product_id'))])
        for s in seatdata:
            if 'payment' not in s.name:
                s.name = s.name+'_no_payment'
        # seatdata.unlink()
        return seat

    @api.model
    def get_unavailable(self, booking):
        seat_obj = self.env['seat.book'].sudo()
        print("check booking ---------------", booking)
        seatdata = seat_obj.search([('booking_date','=', booking.get('booking_date')) ,('book_paid','=',True), ('booking_slot_id','=',booking.get('booking_slot_id'))])
        unavailable = []
        for s in seatdata:
            unavailable.append(s.name)
        return unavailable

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    sequence = fields.Char()
    booking_slot_line_ids = fields.One2many("booking.slot.line", 'order_line_id', string="Booking Slot Line")

    @api.model
    def create(self, vals):
        res = super(PosOrderLine, self).create(vals)
        seat_number = vals.get('seat_number')
        booking_date = vals.get('booking_date')
        booking_slot_id = vals.get('booking_slot_id')
        if vals.get('is_return') and vals.get('combo_item_ids'):
            orig_book = self.env['pos.order.line'].search([('id','=',vals.get('origin_order'))])
            for booking_data in orig_book.booking_slot_line_ids:
                if booking_data.seat_number and booking_data.booking_slot_id.id and booking_data.booking_date:
                    seat_list = booking_data.seat_number.strip('][').replace("'", "").split(',')
                    seats_unbook = self.env['seat.book'].search([('name','in',seat_list),('booking_date','=',booking_data.booking_date),('booking_slot_id','=',booking_data.booking_slot_id.id)])
                    for s in seats_unbook:
                        if 'payment' not in s.name:
                            s.name = s.name+'_no_payment'
                    # seats_unbook.unlink()
        else:
            if vals.get('booking_slot_line_ids'):
                for booking_data in vals.get('booking_slot_line_ids'):
                    combo_data = booking_data[2]
                    if combo_data.get('seat_number') and combo_data.get('booking_date') != '' and combo_data.get('booking_slot_id'):
                        seat_list = combo_data.get('seat_number')
                        seats = self.env['seat.book'].search([('name','in',seat_list),('booking_date','=',combo_data.get('booking_date')),('booking_slot_id','=',combo_data.get('booking_slot_id'))])
                        for s in seats:
                            s.write({
                                'pos_line_id': res.id,
                                'product_id': combo_data.get('product_id'),
                                'book_paid': True
                            })
                    if combo_data.get('last_running_number'):
                        product = self.env['product.template'].browse(combo_data.get('product_id'))
                        if product:
                            product.categ_id.sudo().write({
                                'running_number' : combo_data.get('last_running_number')
                            })
        if seat_number and booking_date != '' and booking_slot_id:
            seat_list = seat_number.strip('][').replace('"', '').split(',')
            seats = self.env['seat.book'].search([('name','in',seat_list),('booking_date','=',booking_date),('booking_slot_id','=',booking_slot_id)])
            for s in seats:
                s.write({
                    'pos_line_id': res.id,
                    'book_paid':True
                })
        return res

class BookingSlotLine(models.Model):
    _name = 'booking.slot.line'
    _description = 'Booking Slot Line'

    uom_id = fields.Many2one('uom.uom', 'Uom', readonly=1)
    booking_slot_id = fields.Many2one("booking.slot", string="Booking Slot")
    booking_date = fields.Date(string="Booking Date")
    seat_number = fields.Char()
    seat_number_return = fields.Char()
    barcode_order = fields.Char()
    seat_barcodes = fields.Char()
    quantity = fields.Float()
    product_id = fields.Many2one('product.product')
    order_line_id = fields.Many2one('pos.order.line', string="POS Order Line")
    last_running_number = fields.Integer()
    barcode = fields.Char()


class PosConfig(models.Model):
    _inherit = "pos.config"

    advance_booking = fields.Integer('Maximum Advance Booking (Days)')
