# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))
        if not self.company_id.sh_disable_follower_confirm_sale:
            for order in self.filtered(
                lambda order: order.partner_id not in
                order.message_partner_ids
            ):
                order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    def message_subscribe(
                        self,
                        partner_ids=None,
                        channel_ids=None,
                        subtype_ids=None
                        ):
        if self.env.company.sh_disable_follower_email and 'manually_added_follower' not in self.env.context:
            return False
        else:
            return super(SaleOrder, self).message_subscribe(
                partner_ids, channel_ids, subtype_ids
            )
