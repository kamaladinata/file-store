# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import datetime
from lxml import etree
import math
import pytz
import threading
import urllib.parse


from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class res_partner(models.Model):
    _inherit = "res.partner"


    birthdate = fields.Date(string='Date Of Birth', default=fields.Datetime.now)

    @api.model
    def _cron_birthday_reminder(self):
        su_id =self.env['res.partner'].browse(SUPERUSER_ID)
        for partner in self.search([]):
            if partner.birthdate:
                bdate =datetime.strptime(partner.birthdate,'%Y-%m-%d').date()
                today =datetime.now().date()
                if bdate != today:
                    if bdate.month == today.month:
                        if bdate.day == today.day:
                            if partner:
                                template_id = self.env['ir.model.data'].get_object_reference(
                                                                    'bi_birthday_reminder',
                                                                    'email_template_edi_birthday_reminder')[1]
                                email_template_obj = self.env['mail.template'].browse(template_id)
                                if template_id:
                                    values = email_template_obj.generate_email(partner.id, fields=None)
                                    values['email_from'] = su_id.email
                                    values['email_to'] = partner.email
                                    values['res_id'] = False
                                    mail_mail_obj = self.env['mail.mail']
                                    msg_id = mail_mail_obj.create(values)
                                    if msg_id:
                                        mail_mail_obj.send([msg_id])
        return True
