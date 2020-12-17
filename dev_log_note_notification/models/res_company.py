# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    model_ids = fields.Many2many('ir.model', string='Applies to')
    notification_to = fields.Selection(selection=[('followers', 'Followers of the Document'),
                                                  ('users', 'Specific Users')], string='Send Notification to',
                                       default='followers',
                                       help=''' * When you select 'Specific Users' at that time notification emails will be \nsent to those users who have 'Allow to receive Log Note Notifications' right''')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: