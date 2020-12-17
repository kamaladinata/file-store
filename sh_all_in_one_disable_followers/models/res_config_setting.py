# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_disable_follower_confirm_sale = fields.Boolean(
        string='Disable to add followers by Confirm Quotation'
        )

    sh_disable_follower_validate_invoice = fields.Boolean(
        string='Disable to add Followers by Validate Invoice/Bill'
        )

    sh_disable_follower_email = fields.Boolean(
        string='Disable to add Followers by Send by Email'
        )

    sh_disable_follower_create_picking = fields.Boolean(
        string='Disable to add Followers by create/update picking'
        )


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_disable_follower_confirm_sale = fields.Boolean(
        string='Disable to add followers by Confirm Quotation',
        related='company_id.sh_disable_follower_confirm_sale',
        readonly=False
        )

    sh_disable_follower_validate_invoice = fields.Boolean(
        string='Disable to add Followers by Validate Invoice/Bill',
        related='company_id.sh_disable_follower_validate_invoice',
        readonly=False
        )

    sh_disable_follower_email = fields.Boolean(
        string='Disable to add Followers by Send by Email',
        related='company_id.sh_disable_follower_email',
        readonly=False
        )

    sh_disable_follower_create_picking = fields.Boolean(
        string='Disable to add Followers by create/update picking',
        related='company_id.sh_disable_follower_create_picking',
        readonly=False
        )
