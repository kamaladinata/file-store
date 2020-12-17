# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, http, tools, _, fields
from odoo.http import request
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, consteq, ustr

import base64
import ast
import json
import logging
import psycopg2
import hashlib
import hmac
from unicodedata import normalize
import werkzeug
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

class PaymentProcessing(PaymentProcessing):

    @http.route(['/payment/process/poll'], type="json", auth="public")
    def payment_status_poll(self):
        # retrieve the transactions
        tx_ids_list = self.get_payment_transaction_ids()

        payment_transaction_ids = request.env['payment.transaction'].sudo().search([
            ('id', 'in', list(tx_ids_list)),
            ('date', '>=', (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        ])
        if not payment_transaction_ids:
            return {
                'success': False,
                'error': 'no_tx_found',
            }

        processed_tx = payment_transaction_ids.filtered('is_processed')
        self.remove_payment_transaction(processed_tx)

        # create the returned dictionnary
        result = {
            'success': True,
            'transactions': [],
        }
        # populate the returned dictionnary with the transactions data
        for tx in payment_transaction_ids:
            message_to_display = tx.acquirer_id[tx.state + '_msg'] if tx.state in ['done', 'pending', 'cancel'] else None
            tx_info = {
                'reference': tx.reference,
                'state': tx.state,
                'return_url': tx.return_url,
                'is_processed': tx.is_processed,
                'state_message': tx.state_message,
                'message_to_display': message_to_display,
                'amount': tx.amount,
                'currency': tx.currency_id.name,
                'acquirer_provider': tx.acquirer_id.provider,
            }
            tx_info.update(tx._get_processing_info())
            result['transactions'].append(tx_info)

        tx_to_process = payment_transaction_ids.filtered(lambda x: x.state == 'done' and x.is_processed is False)
        
        if not tx_to_process:
            auto_invoice = payment_transaction_ids.filtered(lambda x: x.acquirer_id.auto_invoice == True and x.is_processed is False) 
            auto_invoice._auto_invoice()
        try:
            tx_to_process._post_process_after_done()
        except psycopg2.OperationalError as e:
            request.env.cr.rollback()
            result['success'] = False
            result['error'] = "tx_process_retry"
        except Exception as e:
            request.env.cr.rollback()
            result['success'] = False
            result['error'] = str(e)
            _logger.exception("Error while processing transaction(s) %s, exception \"%s\"", tx_to_process.ids, str(e))

        return result
class WebsiteSale(WebsiteSale):

    @http.route(['/action_get_write_date_order'], type="json", auth="none")
    def get_write_date_order(self, **kw):
        # sale_order = request.env['sale.order'].sudo().search([('write_uid','=',kw.get('user_id')),('state','=','draft'),('website_id','!=',False),],order='date_order DESC',limit=1)
        sale_order = request.env['sale.order'].sudo().browse(kw.get('sale_order'))
        if sale_order and sale_order.cart_quantity > 0 and sale_order.state in ['draft','cancel']:
            if not sale_order.transaction_ids:
                for order_line in sale_order.order_line:
                    if order_line.redeem_loyalty:
                        membership_history = request.env['membership.history'].sudo().search([('sale_line_id','=',order_line.id)])
                        for history in membership_history:
                            history.unlink()
                    if order_line.order_id.is_booking_type:
                        seat_book = request.env['seat.book'].sudo().search([('sale_line_id','=',order_line.id)])
                        for seat in seat_book:
                            if 'cart_timeout' not in seat.name:
                                seat.name = seat.name+'_cart_timeout'
                sale_order.action_cancel()
            # sale_order.unlink()
        

    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        bk_qty = kw.get('qty', False)
        if bk_qty:
            set_qty = int(bk_qty)

        res = super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
        bk_plan = kw.get('slot_id', False)
        bk_date = kw.get('bk_date', False)
        
        booking_ids = kw.get('array_data', False)
        if booking_ids:
            booking_ids = json.loads(booking_ids)
        else:
            booking_ids = []
        book_ids = request.env['seat.book'].sudo().browse(booking_ids)

        if booking_ids:
            bk_slot_obj = request.env["booking.slot"].browse([int(bk_plan)])
            sale_order = request.website.sale_get_order()
            order_line = sale_order.order_line.filtered(lambda l: l.product_id.id == int(product_id))
            order_line.write({
                'booking_slot_id' : bk_slot_obj.id,
                # 'price_unit' : bk_slot_obj.price,
                'booking_date' : bk_date if bk_date else None,
            })
            for b in book_ids:
                b.sale_line_id = order_line.id
            sale_order.write({
                'is_booking_type': True,
            })
        return res
        
    @http.route(['/booking/reservation/cart/update_date'], type='json', auth="public", website=True, csrf=False)
    def cart_update_date(self, product_id, **kw):
        print("parameters -----------",kw)
        bk_date = kw.get('booking_date', False)
        line_id = kw.get('line_id', False)
        slot_id = kw.get('slot_id', False)
        vals = {}
        if line_id:
            order_line = request.env['sale.order.line'].sudo().browse(line_id)
            if bk_date:
                vals['booking_date'] =  bk_date if bk_date else None
            if slot_id:
                vals['booking_slot_id'] =  slot_id
            order_line.write(vals)
        return True

    def cart_update_html(self, access_token=False):
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            values['website_sale_order'].website_order_line = values.get('website_sale_order').website_order_line.sorted(key=lambda a:(a.sequence))
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
        View = request.env['ir.ui.view'].sudo()
        return {
            'cart': View.render_template("website_sale.cart_lines", values),
            'total': View.render_template("website_sale.total", values)
        }

    @http.route(['/booking/reservation/cart/update'], type='json', auth="public", website=True, csrf=False)
    def cart_update_book(self, product_id, add_qty=1, set_qty=0, **kw):
        combo_id = kw.get('combo_id', False)
        res = False
        if not combo_id:
            res = self.cart_update(product_id, add_qty, set_qty)
        print("parameters -----------",kw)
        bk_plan = kw.get('booking_slot_id', False)
        bk_date = kw.get('booking_date', False)
        unit_price = kw.get('unit_price', False)
        line_id = kw.get('line_id', False)
        booking_ids = kw.get('seat_ids', False)
        book_ids = request.env['seat.book'].sudo().browse(booking_ids)

        if booking_ids:
            bk_slot_obj = request.env["booking.slot"].sudo().browse([int(bk_plan)])
            sale_order = request.website.sale_get_order()
            order_line = request.env['sale.order.line'].sudo().browse(line_id)
            vals = {
                'booking_slot_id' : bk_slot_obj.id,
                'booking_date' : bk_date if bk_date else None,
            }
            if unit_price:
                vals['price_unit'] = unit_price
            if not order_line.product_id.is_combo:
                order_line.write(vals)
            else:
                combo_item = request.env["booking.slot.line"].sudo().browse(combo_id)
                combo_item.write({
                    'booking_slot_id' : bk_slot_obj.id,
                    'booking_date' : bk_date if bk_date else None,
                })

            for b in book_ids:
                b.sale_line_id = order_line.id
        return self.cart_update_html()
        return res

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        # check = request.website.bk_products_validation()
        # if not check:   
        #     return request.redirect("/shop/cart")
        return super(WebsiteSale, self).checkout(**post)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        # check = request.website.bk_products_validation()
        # if not check:
        #     return request.redirect("/shop/cart")
        order = request.website.sale_get_order()
        if order:
            order.payment_start_date = datetime.now()
        return super(WebsiteSale, self).payment(**post)
    

class BookingReservation(http.Controller):

    
    def get_ipaddress(self):
        return request.httprequest.cookies.get('visitor_uuid')
    
    def generate_barcode(self, prod):
        params = request.env['ir.config_parameter'].sudo()
        prefix = params.get_param('ecom_source')
        activity_type = prod.categ_id.activity_type
        running_number = str(prod.categ_id.running_number)
        prod.categ_id.running_number = 1+prod.categ_id.running_number
        running_number = running_number.zfill(5)
        today = datetime.today().strftime('%d%m%y')
        return activity_type + prefix + today + running_number
    
    # @http.route(['/booking/release'], type="json", auth="none")
    # def releasebook(self, **data):
    #     book = request.env['seat.book'].sudo().search([()])

    @http.route(['/booking/reservation/togglebook'], type="json", auth="none")
    def togglebook(self, **seat):
        seat_obj = request.env['seat.book'].sudo()
        seats = []
        prod = request.env['product.template'].sudo().browse(seat.get('product_id'))
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
                'ip_client': self.get_ipaddress(),
                'sale_line_id': seat.get('line_id'),
                'barcode_order': self.generate_barcode(prod)
            })
            s = {
                'name': seat_new.name,
                'barcode_order': seat_new.barcode_order,
                'book': True,
                'id': seat_new.id
            }
            seats.append(s)
        if seatdata and not seat.get('book'):
            for seat_book in seatdata:
                seats.append({
                    'name': seat_book.name,
                    'barcode_order': seat_book.barcode_order,
                    'book': False,
                    'id':seat_book.id
                })
            seatsunbook = seatdata.sudo()
            for s in seatsunbook:
                if 'payment' not in s.name:
                    s.name = s.name+'_no_payment'
        
        return seats

    @http.route('/scan_ticket/scan_from_main_menu', type='json', auth='user')
    def scan_ticket(self, barcode, **kw):
        """ Receive a barcode scanned from the main menu and return the appropriate
            action (open an existing ticket detail) or warning.
                        var date = today.getDate()+'/'+("0" + (today.getMonth() + 1)).slice(-2)+'/'+today.getFullYear();
        """
        booking = request.env['seat.book'].sudo().search([('barcode_order','=',barcode)])
        scanner_time = datetime.strptime(kw['val']['current_date'],'%d/%m/%Y')
        scanner_date = date.strftime(scanner_time,'%d/%m/%Y')
        attended = 0
        if not booking:
            return {'warning': _('Ticket with barcode %(barcode)s is not recognised on current event. Please check your ticket schedule') % {'barcode': barcode},'type': 'warning','class':'o_notification_warning'}
        for seat in booking:
            if seat.barcode_order == barcode \
                and datetime.strftime(seat.booking_date,'%d/%m/%Y') == scanner_date \
                and seat.booking_slot_id.time_slot_id.id == kw['val']['time_slot_id'] \
                and seat.product_id.name == kw['val']['ticket_name'] \
                and seat.attended == False:
                seat.attended = True
                attended = 1
            elif seat.barcode_order == barcode \
                and datetime.strftime(seat.booking_date,'%d/%m/%Y') == scanner_date \
                and seat.booking_slot_id.time_slot_id.id == kw['val']['time_slot_id'] \
                and seat.product_id.name == kw['val']['ticket_name'] \
                and seat.attended == True:
                attended = 2
        if attended == 1:
            return {'val': kw['val'],'warning': _('Ticket with barcode %(barcode)s is valid') % {'barcode': barcode}, 'type' : 'success', 'class':'o_notification_success'}
        elif attended == 2:
            return {'warning': _('Ticket with barcode %(barcode)s has been utilised') % {'barcode': barcode},'type' : 'danger','class':'o_notification_danger'}
        else:
            return {'warning': _('Ticket with barcode %(barcode)s is not recognised on current event. Please check your ticket schedule') % {'barcode': barcode},'type': 'warning','class':'o_notification_warning'}

    
    @http.route('/scan_ticket/attendance_count', type='json', auth='user')
    def attend_count(self, vals):
        """ Receive a barcode scanned from the main menu and return the appropriate
            action (open an existing ticket detail) or warning.
                        var date = today.getDate()+'/'+("0" + (today.getMonth() + 1)).slice(-2)+'/'+today.getFullYear();
        """
        current_datetime = datetime.strptime(vals['current_date'],'%d/%m/%Y')
        current_date = date.strftime(current_datetime,'%Y-%m-%d')
        if vals['start_time'] == 'NaN:NaN':
            return
        elif vals['time_slot_id'] and vals['ticket_name']:
            attend = request.env['seat.book'].search_count([('booking_date','=',current_date), \
                ('booking_slot_id.time_slot_id.id','=',vals['time_slot_id']),\
                ('product_order.name','=',vals['ticket_name']),\
                ('attended','=',True)])
        return attend

    def get_all_week_days(self, sel_date, product_obj):
        """Return all week day,date list for the selected date"""
        bk_open_days = product_obj.get_bk_open_closed_days("open")
        if not bk_open_days:
            return False
        week_days = [None]*7
        end_date = product_obj.br_end_date
        current_date = self.get_default_date(product_obj.id)
        day = sel_date.weekday()
        v_date = sel_date - timedelta(days=day)
        for w_day in week_days:
            day = v_date.weekday()
            week_days[day] = {
                "day" : Days[day],
                "date_str" : datetime.strftime(v_date,'%d %b %Y'),
                "date" : datetime.strftime(v_date,'%Y-%m-%d'),
                "state" : "active" if current_date <= v_date and v_date <= end_date and Days[day] in bk_open_days else "inactive",
            }
            v_date = v_date + timedelta(days=1)
        return week_days


    # Update slots on week day selection
    @http.route(['/booking/reservation/update/slots'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_update_slots(self,**post):
        w_day = post.get('w_day',False)
        w_date = post.get('w_date',False)
        w_date = datetime.strptime(w_date,'%Y-%m-%d').date()
        product_id = post.get('product_id',False)
        if not product_id:
            return False
        product_obj = request.env["product.template"].sudo().browse(product_id)
        current_day_slots = product_obj.get_booking_slot_for_day(w_date)
        values = {
            'day_slots' : current_day_slots,
            'current_date' : w_date,
            'product' : product_obj,
        }
        return request.env.ref("movie_booking_system.booking_modal_bk_slots_n_plans_div").render(values, engine='ir.qweb')

    # Update plans on slot selection
    @http.route(['/booking/reservation/slot/plans'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_slot_plans(self,**post):
        sel_date = post.get('sel_date',False)
        sel_date = datetime.strptime(sel_date,'%Y-%m-%d').date()
        time_slot_id = post.get('time_slot_id',False)
        slot_plans = post.get('slot_plans',False)
        product_id = post.get('product_id',False)
        user_id = post.get('user_id',False)
        line_id = post.get('line_id',False)
        seat = post.get('seat',False)
        product_obj = request.env["product.template"].sudo().browse(product_id);
        slot_plans = ast.literal_eval(slot_plans)
        values = {
            'd_plans' : slot_plans,
            'current_date' : sel_date,
            'product' : product_obj,
        }
        book_data = {
            'user_id':user_id,
            'product_id':product_id,
            'ip_client': self.get_ipaddress(),
            'line_id':line_id
        }
        request.env['seat.book'].sudo().browse(seat).unlink()
        request.env['seat.book'].sudo().cleannotpaid(book_data)
        return request.env.ref("movie_booking_system.booking_sel_plans").render(values, engine='ir.qweb')

    def get_default_date(self, product_id):
        product_obj = request.env["product.template"].sudo().browse(product_id);
        w_open_days = product_obj.get_bk_open_closed_days("open")
        print("cehck  open days-----------",w_open_days)
        if not w_open_days:
            return False
        current_date = date.today()
        start_date = product_obj.br_start_date
        end_date = product_obj.br_end_date
        print("cehck  date-----------",w_open_days,current_date, start_date,end_date)
        if end_date < current_date:
            return False
        elif current_date < start_date:
            current_date = start_date
        current_day = Days[current_date.weekday()]
        if current_day in w_open_days:
            return current_date
        print("cehck open dayss-----------",w_open_days)
        print("current day-----------",current_day)
        while(current_day not in w_open_days):
            current_date = current_date + timedelta(days=1)
            current_day = Days[current_date.weekday()]
            if end_date < current_date:
                return False
        return current_date

    # Append booking Pop-Up modal
    @http.route(['/booking/reservation/modal'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_modal(self,**post):
        product_id = post.get('product_id',False)
        line_id = post.get('line_id',False)
        if not product_id:
            return False
        product_obj = request.env["product.template"].sudo().browse(product_id)
        values = {
            'booking_status' : False
        }
        current_date = self.get_default_date(product_id)
        params = request.env['ir.config_parameter'].sudo()
        if current_date:
            week_days = self.get_all_week_days(current_date, product_obj)
            current_day = Days[current_date.weekday()]
            end_date = product_obj.br_end_date
            current_day_slots = product_obj.get_booking_slot_for_day(current_date)
            w_closed_days = product_obj.get_bk_open_closed_days("closed")
            blocked_date = product_obj.blocked_date

            values.update({
                'booking_status' : True,
                'product' : product_obj,
                'week_days' : week_days,
                'w_closed_days' : json.dumps(w_closed_days),
                'current_day' : current_day,
                'current_date' : current_date,
                'day_slots' : current_day_slots,
                'end_date' : end_date,
                'default_date' : current_date,
                'max_booking': int(params.get_param('max_booking_in_advance')),
                'blocked_date' : blocked_date,
            })
        if line_id:
            seats = []
            line = request.env['sale.order.line'].sudo().browse(line_id)
            # if line.is_combo:
            seats_book = request.env['seat.book'].sudo().search([('sale_line_id','=',line_id)])
            combo_id = post.get('combo_id',False)
            combo = False
            if combo_id:
                combo = request.env["booking.slot.line"].sudo().browse(combo_id)
                seats_book = request.env['seat.book'].sudo().search([('sale_line_id','=',line_id),('product_id','=',combo.product_id.id)])
            for s in seats_book:
                seats.append(s.id)

            if not line.product_id.is_combo:
                values.update({
                    'booking_slot_id': line.booking_slot_id.id,
                    'default_date': line.booking_date,
                    'seats': json.dumps(seats),
                    'qty': line.product_uom_qty,
                    'price': line.price_unit
                })
                if line.booking_date:
                        values.update({
                            'default_date': line.booking_date,
                        })
            else:
                if combo:
                    values.update({
                        'booking_slot_id': combo.booking_slot_id.id,
                        'seats': json.dumps(seats),
                        'qty': combo.quantity,
                        'price': combo.product_id.lst_price
                    })
                    if combo.booking_date:
                        values.update({
                            'default_date': combo.booking_date,
                        })
            
        print("check values =======",values)
        return request.env.ref("movie_booking_system.booking_and_reservation_modal_temp").render(values, engine='ir.qweb')

    @http.route(['/reservation/clearbook'], type='json', auth="public", website=True)
    def clearbook(self,**post):
        line_id = post.get('line_id',False)
        seatbook = request.env["seat.book"].sudo().browse(line_id)
        seats = seatbook.sudo()
        for s in seats:
            if 'payment' not in s.name:
                s.name = s.name+'_no_payment'
        # seatbook.sudo().unlink()

    # Update booking modal on date selection
    @http.route(['/booking/reservation/modal/update'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_modal_update(self,**post):
        product_id = post.get('product_id',False)
        new_date = post.get('new_date',False)
        slot_id = post.get('slot_id',False)
        user_id = post.get('user_id',False)
        line_id = post.get('line_id',False)
        seat_data = post.get('array_data',False)
        if not product_id:
            return False
        product_obj = request.env["product.template"].sudo().browse(product_id);
        new_date = datetime.strptime(new_date,'%d/%m/%Y').date()
        end_date = product_obj.br_end_date

        week_days = self.get_all_week_days(new_date, product_obj)
        current_day = Days[new_date.weekday()]
        current_day_slots = product_obj.get_booking_slot_for_day(new_date)

        values = {
            'product' : product_obj,
            'week_days' : week_days if week_days else [],
            'current_day' : current_day,
            'current_date' : new_date,
            'day_slots' : current_day_slots,
            'end_date' : end_date,
            'slot_id': slot_id
        }
        book_data = {
            'user_id':user_id,
            'product_id':product_id,
            'ip_client': self.get_ipaddress(),
            'line_id':line_id
        }
        if not seat_data:
            request.env['seat.book'].sudo().cleannotpaid(book_data)
        return request.env.ref("movie_booking_system.booking_modal_bk_slots_main_div").render(values, engine='ir.qweb')

    @http.route(['/booking/reservation/cart/validate'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_cart_validate(self, **post):
        product_id = post.get('product_id', False)
        booking_ids = post.get('booking_ids', False)
        book_ids = request.env['seat.book'].sudo().browse(booking_ids)
        sale_order = request.website.sale_get_order()
        if sale_order:
            order_line = sale_order.order_line.filtered(lambda l: l.product_id.product_tmpl_id.id == int(product_id))    
            return False if len(order_line) else True
        return True
