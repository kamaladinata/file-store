# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseDownPayment(models.TransientModel):
    _name = 'purchase.down.payment'
    _description = "Purchase Down Payment"

    @api.multi
    def create_bill(self):
        self.purchase_id.down_payment_by = self.down_payment_by
        self.purchase_id.amount = self.amount

        if self.purchase_id.down_payment_by in ['fixed', 'percentage']:
            if self.amount <= 0:
                raise ValidationError(_('''Amount must be positive'''))
            if self.purchase_id.down_payment_by == 'percentage':
                payment = self.purchase_id.amount_total * self.purchase_id.amount / 100
            else:
                payment = self.amount

            if self.purchase_id.total_invoices_amount == 0:
                if payment > self.purchase_id.amount_total:
                    raise ValidationError(_('''You are trying to pay: %s, but\n You can not pay more than: %s''') % (payment, self.purchase_id.amount_total))
            if self.purchase_id.total_invoices_amount == self.purchase_id.amount_total:
                raise ValidationError(_('''Bills worth %s already created for this purchase order, check attached bills''') % (self.purchase_id.amount_total))
            if self.purchase_id.total_invoices_amount > 0:
                remaining_amount = self.purchase_id.amount_total - self.purchase_id.total_invoices_amount
                if payment > remaining_amount:
                    raise ValidationError(_('''You are trying to pay: %s, but\n You have already paid: %s for purchase order worth: %s''') % (payment, self.purchase_id.total_invoices_amount, self.purchase_id.amount_total))
            if payment > self.purchase_id.amount_total:
                raise ValidationError(_('''You are trying to pay: %s, but\n You can not pay more than: %s''') % (payment, self.purchase_id.amount_total))

        journal_id = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.purchase_id.company_id.id)], limit=1)
        if journal_id:
            self.purchase_id.dp_journal_id = journal_id.id
        else:
            raise ValidationError(_('''Please configure at least one Purchase Journal for %s Company''') % (self.purchase_id.company_id.name))

        product_id = (self.env.user.company_id.down_payment_product_id or False)
        if not product_id:
            raise ValidationError(_('''Please configure Advance Payment Product into : Purchase > Settings'''))

        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]

        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice',
                             'default_purchase_id': self.purchase_id.id,
                             'default_currency_id': self.purchase_id.currency_id.id,
                             'default_company_id': self.purchase_id.company_id.id,
                             'company_id': self.purchase_id.company_id.id}
        # choose the view_mode accordingly
        if len(self.purchase_id.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.purchase_id.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.purchase_id.invoice_ids.id or False
        return result

    down_payment_by = fields.Selection(selection=[('deduct_down_payment', 'Billable lines (deduct previous payments if any)'),
                                                  ('partial_invoice', 'Partial Invoice (not down payment)'),
                                                  ('fixed', 'Advance payment (fixed amount)')],
                                       string='What do you want to bill?', default='deduct_down_payment')
    #('dont_deduct_down_payment', 'Billable lines'), ('percentage', 'Advance payment (percentage)'),
    amount = fields.Float(string='Amount')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: