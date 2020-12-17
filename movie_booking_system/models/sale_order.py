# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta,date

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def unlink(self):
        for line in self:
            seats = self.env['seat.book'].search([('sale_line_id','=', line.id)])
            seats.unlink()
        return super(SaleOrderLine, self).unlink()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def check_payment_expired(self,order_date):
        today = date.today()
        date_expired = self.get_payment_expired(order_date).date()
        if today == date_expired:
            return True
        else:
            return False
            
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            for line in so.order_line:
                membership_history = self.env['membership.history'].sudo().search([('sale_line_id','=',line.id)])
                for history in membership_history:
                    history.unlink()
        return res

    def get_payment_expired(self,order_date):
        return (order_date + timedelta(int(self.env['ir.config_parameter'].get_param('payment_expired'))))

    def _send_order_confirmation_mail(self):
        # to avoid send email SO when user pay
        if self.website_id:
            return True
        else:
            return super(SaleOrder, self)._send_order_confirmation_mail()


class AccountMove(models.Model):

    _inherit = 'account.move'

    def get_payment_expired(self,order_date):
        return self.env['sale.order'].get_payment_expired(order_date).strftime('%d-%m-%Y')