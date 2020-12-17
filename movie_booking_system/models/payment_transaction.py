from odoo import api, http, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta
import datetime, pytz
import base64, json
import traceback


import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        seat_ids = self.env['seat.book'].sudo().search([('sale_line_id','=',self.id)])
        seats_barcodes = []
        for s in seat_ids:
            seats_barcodes.append({
                "barcode_order": s.barcode_order,
                "book": True,
                "name": s.name
            })
        if seats_barcodes:
            res.update({
                'seat_barcodes': json.dumps(seats_barcodes) 
            })
        res.update({
            'booking_date': self.booking_date,
            'booking_slot_id': self.booking_slot_id.id
            })
        return res

class Payment(models.Model):
    _inherit = "payment.acquirer"

    auto_invoice = fields.Boolean(string="Auto Invoice Offline Payment")

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _reconcile_after_transaction_done(self):
        super(PaymentTransaction, self)._reconcile_after_transaction_done()
        email_template = self.env.ref('movie_booking_system.mail_template_ticket')
        invoices = self.mapped('invoice_ids').filtered(lambda inv: inv.state == 'posted')
        if email_template:
            for trans in self:
                for sale_order in trans.sale_order_ids:
                    if sale_order.is_attraction():
                        for invoice in invoices:
                            ir_attachment_ids = []
                            for so_line in sale_order.order_line:
                                
                                seat_books = self.env['seat.book'].search([('sale_line_id','=',so_line.id)])
                                for seat_book in seat_books:
                                    pdf = self.env.ref('movie_booking_system.ticket_movie_book').render_qweb_pdf(seat_book.id)
                                    b64_pdf = base64.b64encode(pdf[0])
                                    seat_book.sudo().book_paid = True
                                    ir_attachment = self.env['ir.attachment'].create({
                                        'name': 'Ticket_%s_Movie_%s' % (invoice.name,seat_book.name.upper()),
                                        'type': 'binary',
                                        'datas': b64_pdf,
                                        'res_model': 'account.move',
                                        'res_id': invoice.id,
                                        'mimetype': 'application/pdf'
                                    })
                                    ir_attachment_ids.append(ir_attachment.id)
                            email_template.update({
                                'attachment_ids' : [(6,0,ir_attachment_ids)]
                            })
                            mail_id = email_template.send_mail(invoice.id,force_send=False)
                            mail_obj = self.env['mail.mail'].sudo().browse(mail_id)
                            if mail_obj and mail_obj.state == 'outgoing':
                                mail_obj.send()

    def _auto_invoice(self):
        sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
        for tx in self:
            tx._check_amount_and_confirm_order()
        # send order confirmation mail
        sales_orders._send_order_confirmation_mail()
        # invoice the sale orders if needed
        self._invoice_sale_orders()
        invoices = self.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
        invoices.post()
        # reminder : sale order empty same case local and live
        for sale_order in sales_orders:
            is_membership = sale_order.check_so_is_membership()
            if is_membership:
                # confirm so and create invoice
                for invoice in invoices:
                    for line in invoice.invoice_line_ids:
                        membership = self.env['membership.membership_line'].sudo().search([('account_invoice_line','=',line.id)])
                        membership.sudo().write({
                            'duration': sale_order.duration,
                            'member_price': sale_order.member_price
                        }) 

        for inv in invoices:
            inv.sudo().invoice_payment_ref = inv.name

        if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            default_template = self.env.ref('movie_booking_system.email_template_edi_invoice_ecommerce')
            # default_template = self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
            if default_template:
                for trans in self.filtered(lambda t: t.sale_order_ids):
                    ctx_company = {'company_id': trans.acquirer_id.company_id.id,
                                   'force_company': trans.acquirer_id.company_id.id,
                                   'mark_invoice_as_sent': True,
                                   }
                    trans = trans.with_context(ctx_company)
                    for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                        default_template.send_mail(invoice.id,force_send=True)
                        # invoice.message_post_with_template(int(default_template), email_layout_xmlid="mail.mail_notification_paynow")