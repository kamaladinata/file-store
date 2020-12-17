# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models,  _


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _prepare_email_body(self, chatter_log_message, logged_in_user_id, partner_id, document_name):
        email_body = (_('''<div style="background-color:#F3F5F6;color:#515166;font-family:Arial,Helvetica,sans-serif;font-size:14px;">'''))
        email_body += (_('''<br/>'''))
        email_body += (_('''Hello, %s''') % (partner_id.name))
        email_body += (_('''<br/><br/>'''))
        email_body += (_('''<b>%s</b> recently Logged a Note on <b>%s</b> document, below is the Logged Note''') % (logged_in_user_id.name, document_name))
        email_body += (_('''<br/><br/>'''))
        email_body += (_('''<b>Logged Note : </b> %s''') % (chatter_log_message))
        email_body += (_('''<br/><br/>'''))
        email_body += (_('''Thank You.'''))
        email_body += (_('''<div>'''))
        return email_body

    def send_notification_to_followers(self, parent_id, chatter_log_message, logged_in_user_id):
        for follower_id in parent_id.message_follower_ids:
            if follower_id.partner_id and follower_id.partner_id.email:
                document_name = parent_id.name or 'None'
                email_body = self._prepare_email_body(chatter_log_message, logged_in_user_id, follower_id.partner_id, document_name)
                subject = (_('''Note Logged on a document (%s)''') % (document_name))
                email_id = self.env['mail.mail'].create(
                    {'subject': subject,
                     'email_from': self.env.user.company_id.email,
                     'email_to': follower_id.partner_id.email,
                     'message_type': 'email',
                     'body_html': email_body,
                     })
                email_id.send()

    def send_notification_to_users(self, chatter_log_message, parent_id, logged_in_user_id):
        authorized_group_id = self.env.ref('dev_log_note_notification.will_receive_log_note_notification')
        if authorized_group_id and authorized_group_id.users:
            for user in authorized_group_id.users:
                if user.partner_id and user.partner_id.email:
                    document_name = parent_id.name or 'None'
                    email_body = self._prepare_email_body(chatter_log_message, logged_in_user_id, user.partner_id, document_name)
                    subject = (_('''Note Logged on a document (%s)''') % (document_name))
                    email_id = self.env['mail.mail'].create({'subject': subject,
                                                             'email_from': self.env.user.company_id.email,
                                                             'email_to': user.partner_id.email,
                                                             'message_type': 'email',
                                                             'body_html': email_body
                                                             })
                    email_id.send()

    def create(self, vals):
        res = super(MailMessage, self).create(vals)
        company_id = self.env.company or False
        logged_in_user_id = self.env.user
        if logged_in_user_id.id != 1:
            if res.res_id and res.body:
                if isinstance(vals,dict):
                    vall = vals
                else:
                    vall = vals[0]
                    
                if 'model' in vall:
                    if res.subtype_id and res.subtype_id.name == 'Note':
                        if res.message_type and res.message_type == 'comment':
                            if company_id and logged_in_user_id:
                                applicable_models = []
                                if company_id.model_ids:
                                    for valid_model in company_id.model_ids:
                                        applicable_models.append(valid_model.model)
                                if applicable_models:
                                    parent_id = self.env[vall['model']].browse(int(res.res_id))
                                    if parent_id._name in applicable_models:
                                        if company_id.notification_to == 'followers':
                                            if parent_id and parent_id.message_follower_ids:
                                                self.send_notification_to_followers(parent_id, res.body, logged_in_user_id)
                                        if company_id.notification_to == 'users':
                                            self.send_notification_to_users(res.body, parent_id, logged_in_user_id)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
