# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def get_purchase_total_invoices_amount(self):
        for purchase in self:
            if purchase.invoice_ids:
                payment = 0
                for bill in purchase.invoice_ids:
                    payment += bill.amount_total
                purchase.total_invoices_amount = payment

    @api.multi
    def hide_create_bill_status(self):
        for purchase in self:
            hide_create_bill = False
            if purchase.total_invoices_amount >= purchase.amount_total:
                hide_create_bill = True
            for line in purchase.order_line:
                if line.qty_received > line.qty_invoiced:
                    hide_create_bill = False
                    break
            purchase.hide_create_bill = hide_create_bill

    total_invoices_amount = fields.Float(
        string='Advance Payment Amount', compute='get_purchase_total_invoices_amount')
    down_payment_by = fields.Selection(
        selection=[('deduct_down_payment', 'Billable lines (deduct previous payments if any)'),
                   ('partial_invoice', 'Partial Invoice (not down payment)'),
                   ('fixed', 'Advance payment (fixed amount)')],
        string='What do you want to bill?', copy=False)
    #('dont_deduct_down_payment', 'Billable lines'),
    #('percentage', 'Advance payment (percentage)'),
    amount = fields.Float(string='Amount', copy=False)
    dp_journal_id = fields.Many2one('account.journal', string='Journal', copy=False)
    hide_create_bill = fields.Boolean(
        string='Hide Create Bill', copy=False, compute='hide_create_bill_status')

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'order_line' not in default:
            default['order_line'] = [
                (0, 0, line.copy_data()[0]) for line in self.order_line.filtered(
                    lambda l: not l.is_down_payment)]
        return super(PurchaseOrder, self).copy_data(default)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_down_payment = fields.Boolean(string='Advance Payment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
