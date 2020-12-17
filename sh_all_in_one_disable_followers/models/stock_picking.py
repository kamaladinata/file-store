# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def message_subscribe(
            self,
            partner_ids=None,
            channel_ids=None,
            subtype_ids=None
            ):
        if self.env.company.sh_disable_follower_create_picking and 'manually_added_follower' not in self.env.context:
            return False
        else:
            return super(StockPicking, self).message_subscribe(
                partner_ids,
                channel_ids,
                subtype_ids
                )