# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    activity_due_notification = fields.Boolean("Due Activity Notification")
    ondue_date_notify = fields.Boolean("On Due Date")
    after_first_notify = fields.Boolean("Days After Due Date")
    before_first_notify = fields.Boolean("Days Before Due Date")
    enter_after_first_notify = fields.Integer("Enter Days After Due Date")
    enter_before_first_notify = fields.Integer("Enter Days Before Due Date")
    # after_second_notify = fields.Boolean("Second Days After Due Date")
    # before_second_notify = fields.Boolean("Second Days Before Due Date")
    # enter_after_second_notify = fields.Integer("Enter Second Days After Due Date")
    # enter_before_second_notify = fields.Integer("Enter Second Days Before Due Date")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    activity_due_notification = fields.Boolean("Due Activity Notification",
        related='company_id.activity_due_notification', readonly=False )
    ondue_date_notify = fields.Boolean("On Due Date",
        related='company_id.ondue_date_notify', readonly=False)
    after_first_notify = fields.Boolean("Days After Due Date",
        related='company_id.after_first_notify', readonly=False)
    before_first_notify = fields.Boolean("Days Before Due Date",
        related='company_id.before_first_notify', readonly=False)
    enter_after_first_notify = fields.Integer("Enter Days After Due Date",
        related='company_id.enter_after_first_notify', readonly=False)
    enter_before_first_notify = fields.Integer("Enter Days Before Due Date",
        related='company_id.enter_before_first_notify', readonly=False)
    # after_second_notify = fields.Boolean("Second Days After Due Date",related='company_id.after_second_notify',readonly=False)
    # before_second_notify = fields.Boolean("Second Days Before Due Date",related='company_id.before_second_notify',readonly=False)
    # enter_after_second_notify = fields.Integer("Enter Second Days After Due Date",related='company_id.enter_after_second_notify',readonly=False)
    # enter_before_second_notify = fields.Integer("Enter Second Days Before Due Date",related='company_id.enter_before_second_notify',readonly=False)

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    text_note = fields.Char("Notes In Char format ", compute ='get_html_to_char_note')

    @api.depends('note')
    def get_html_to_char_note(self):
        if self and self.note:
            self.text_note = html2plaintext(self.note)

    @api.model
    def notify_mail_activity_fun(self):
        template = self.env.ref('sh_acitivity_notification.template_mail_activity_due_notify_email')
        company_object = self.env['res.company'].search([('activity_due_notification','=',True)], limit=1)
        if template and company_object and company_object.activity_due_notification:
            activity_obj = self.env['mail.activity'].search([])
            if activity_obj:
                for record in activity_obj:
                    if record.date_deadline and record.user_id and record.user_id.commercial_partner_id and record.user_id.commercial_partner_id.email :
                        deadline = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date()
                        # On Due Date
                        if company_object.ondue_date_notify:
                            if datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() == datetime.now().date() :
                                mail_res = template.send_mail(record.id,force_send=True)
                        # On After First Notify
                        if company_object.after_first_notify and company_object.enter_after_first_notify :
                            after_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() + timedelta(days= company_object.enter_after_first_notify)
                            if deadline < datetime.now().date() <= after_date:
                                _logger.info('Send after due email')
                                mail_res = template.send_mail(record.id,force_send=True)
                        # On Before First Notify
                        if company_object.before_first_notify and company_object.enter_before_first_notify :
                            before_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() - timedelta(days= company_object.enter_before_first_notify)
                            if deadline > datetime.now().date() >= before_date:
                                _logger.info('Send before due email')
                                mail_res = template.send_mail(record.id,force_send=True)
                        # On After Second Notify
                        # if company_object.after_second_notify and company_object.enter_after_second_notify :
                        #     after_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() + timedelta(days= company_object.enter_after_second_notify)
                        #     if after_date == datetime.now().date() :
                        #         mail_res = template.send_mail(record.id,force_send=True)
                        # On Before Second Notify
                        # if company_object.before_second_notify and company_object.enter_before_second_notify :
                        #     before_date = datetime.strptime(str(record.date_deadline), DEFAULT_SERVER_DATE_FORMAT).date() - timedelta(days= company_object.enter_before_second_notify)
                        #     if before_date == datetime.now().date() :
                        #         mail_res = template.send_mail(record.id,force_send=True)
