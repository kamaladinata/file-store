# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def message_subscribe(
            self,
            partner_ids=None,
            channel_ids=None,
            subtype_ids=None
            ):
        if self.env.company.sh_disable_follower_email and 'manually_added_follower' not in self.env.context:
            return False
        else:
            return super(PurchaseOrder, self).message_subscribe(
                partner_ids,
                channel_ids,
                subtype_ids
                )
