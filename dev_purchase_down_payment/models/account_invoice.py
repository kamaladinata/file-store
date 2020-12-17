# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import time


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        if line.is_down_payment and not res.get('quantity'):
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            res.update({'quantity': qty})
        if line.order_id.down_payment_by == 'dont_deduct_down_payment':
            if line.is_down_payment:
                return {}
            #else:
            #    res.update({'quantity': line.qty_received-line.qty_invoiced})
        if line.order_id.down_payment_by == 'deduct_down_payment':
            if line.is_down_payment:
                if not line.qty_invoiced:
                    return {}
                else:
                    res.update({'quantity': -1})
            #else:
            #    res.update({'quantity': line.qty_received-line.qty_invoiced})
        if line.order_id.down_payment_by == 'partial_invoice':
            if not line.is_down_payment:
                new_qty = line.order_id.amount * res.get('quantity') / 100
                res.update({'quantity': new_qty})
        return res

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        if not self.invoice_line_ids:
            #as there's no invoice line yet, we keep the currency of the PO
            self.currency_id = self.purchase_id.currency_id

        adv_product_id = (self.company_id.down_payment_product_id or False)
        if not adv_product_id:
            raise ValidationError(_('''Please configure Advance Payment Product into : Purchase > Settings'''))

        new_lines = self.env['account.invoice.line']

        if self.purchase_id.down_payment_by == 'dont_deduct_down_payment':
            for line in self.purchase_id.order_line - self.invoice_line_ids.mapped(
                'purchase_line_id'):
                if line.product_id.id == adv_product_id.id or line.qty_received > line.qty_invoiced:
                    data = self._prepare_invoice_line_from_po_line(line)
                    if data:
                        new_line = new_lines.new(data)
                        new_line._set_additional_fields(self)
                        new_lines += new_line
        elif self.purchase_id.down_payment_by == 'deduct_down_payment':
            for line in self.purchase_id.order_line:
                if line.product_id.id == adv_product_id.id or line.qty_received > line.qty_invoiced:
                    data = self._prepare_invoice_line_from_po_line(line)
                    if data:
                        new_line = new_lines.new(data)
                        new_line._set_additional_fields(self)
                        new_lines += new_line
        elif self.purchase_id.down_payment_by == 'partial_invoice':
            for line in self.purchase_id.order_line:
                if line.product_id.id == adv_product_id.id or line.qty_received > line.qty_invoiced:
                    data = self._prepare_invoice_line_from_po_line(line)
                    if data:
                        new_line = new_lines.new(data)
                        new_line._set_additional_fields(self)
                        new_lines += new_line
        elif self.purchase_id.down_payment_by in ['fixed', 'percentage']:
            amount = self.purchase_id.amount
            if self.purchase_id.down_payment_by == 'percentage':
                amount = self.purchase_id.amount_total * self.purchase_id.amount / 100

            # EDIT move to account invoice line so when discarding uncreated invoice it won't add more line
            # po_line_obj = self.env['purchase.order.line']
            # po_line = po_line_obj.create({'name': _('Advance: %s') % (time.strftime('%m %Y'),),
            #                               'price_unit': amount,
            #                               'product_qty': 0.0,
            #                               'order_id': self.purchase_id.id,
            #                               'product_uom': adv_product_id.uom_id.id,
            #                               'product_id': adv_product_id.id,
            #                               'date_planned': self.purchase_id.date_order,
            #                               'is_down_payment': True
            #                               })

            invoice_line = self.env['account.invoice.line']
            date = self.date or self.date_invoice
            price_unit = self.purchase_id.currency_id._convert(
                amount, self.currency_id, self.purchase_id.company_id,
                date or fields.Date.today(), round=False)
            data = {'product_id': adv_product_id.id or False,
                    'name': _('Advance Payment'),
                    'account_id': invoice_line.with_context(
                        {'journal_id': self.purchase_id.dp_journal_id.id,
                         'type': 'in_invoice'})._default_account(), 'price_unit': amount,
                    'quantity': 1,
                    'price_unit': price_unit or amount,
                    # 'purchase_line_id': po_line.id
                    }
            account = invoice_line.get_invoice_line_account(
                'in_invoice', adv_product_id, self.purchase_id.fiscal_position_id,
                self.env.user.company_id)
            if account:
                data['account_id'] = account.id
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.purchase_id.payment_term_id
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        return {}
  
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        res = super(AccountInvoiceLine, self).create(vals)
        purchase_id = res.invoice_id.po_id
        if purchase_id:
            if purchase_id.down_payment_by in ['fixed', 'percentage']:
                adv_product_id = (purchase_id.company_id.down_payment_product_id or False)

                if adv_product_id==self.env['product.product'].browse(vals.get('product_id',False)):
                    amount = purchase_id.amount
                    if purchase_id.down_payment_by == 'percentage':
                        amount = purchase_id.amount_total * purchase_id.amount / 100

                    po_line_obj = self.env['purchase.order.line']
                    po_line = po_line_obj.create({'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                                                  'price_unit': amount,
                                                  'product_qty': 0.0,
                                                  'order_id': purchase_id.id,
                                                  'product_uom': adv_product_id.uom_id.id,
                                                  'product_id': adv_product_id.id,
                                                  'date_planned': purchase_id.date_order,
                                                  'is_down_payment': True
                                                  })
                    res.update({'purchase_line_id': po_line.id})
        return res
        


    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
