# -*- coding: utf-8 -*-

import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class mail_thread(models.AbstractModel):
    """
    Overwrite to redefine message routing and process corresponding exceptions
    """
    _inherit = "mail.thread"

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        """
        Overwrite to catch and mark unattached messages

        1. Send notificaion if defined in settings
        """
        res = []
        try:
            res = super(mail_thread, self).message_route(
                message, message_dict, model=model,
                thread_id=thread_id, custom_values=custom_values
            )
        except ValueError:
            message_dict['is_unattached'] = True
            message_id = self._create_lost_message(**message_dict)
            _logger.warning(u"Message {} can't be routed. Assign it to 'lost messages'".format(message_id))
            # 1
            Config = self.env['ir.config_parameter'].sudo()
            notify_about_lost_messages = safe_eval(Config.get_param("notify_about_lost_messages", "False"))
            if notify_about_lost_messages:
                notify_lost_user_ids =  safe_eval(Config.get_param("notify_lost_user_ids", "[]"))
                if notify_lost_user_ids:
                    try:
                        users = self.env["res.users"].sudo().browse(notify_lost_user_ids)
                        email_to = users.mapped("email")
                        mail_server = self.env['ir.mail_server'].sudo()
                        context = self.env.context.copy()
                        action = self.env.ref("mail_manual_routing.action_unattached_mail_open_only_form").id
                        base_url = Config.get_param('web.base.url')
                        db = self.env.cr.dbname
                        url = "{}/web?db={}#id={}&action={}".format(base_url, db, message_id.id, action)
                        context.update({"url": url})
                        template = self.env.ref('mail_manual_routing.lost_message_notification_template')
                        body_html = template.with_context(context)._render_template(
                            template.body_html,
                            'mail.message',
                            message_id.id,
                        )
                        subject = template.subject
                        message = mail_server.build_email(
                            email_from=self.env.user.email,
                            subject=subject,
                            body=body_html,
                            subtype='html',
                            email_to=email_to,
                        )
                        mail_server.send_email(message)
                    except Exception as e:
                        _logger.error("Notification by lost message {} is not sent. Reason: {}".format(message_id, e))
        return res

    @api.returns('mail.message', lambda value: value.id)
    def _create_lost_message(self, *,
                             body='', subject=None, message_type='notification',
                             email_from=None, author_id=None, parent_id=False,
                             subtype_id=False, subtype=None, partner_ids=None, channel_ids=None,
                             attachments=None, attachment_ids=None,
                             add_sign=True, record_name=False,
                             **kwargs):
        """
        The method to prepare lost message and create it.
        It represents a modified copy of message_post 
        """
        msg_kwargs = dict((key, val) for key, val in kwargs.items() if key in self.env['mail.message']._fields)
        author_info = self._message_compute_author(author_id, email_from, raise_exception=True)
        author_id, email_from = author_info['author_id'], author_info['email_from']
        if not subtype_id:
            subtype = subtype or 'mt_note'
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)
        values = dict(msg_kwargs)
        values.update({
            'author_id': author_id,
            'email_from': email_from,
            'model': False,
            'res_id': False,
            'body': body,
            'subject': subject or False,
            'message_type': message_type,
            'parent_id': parent_id,
            'subtype_id': subtype_id,
            'partner_ids': set(partner_ids or []),
            'channel_ids': set(channel_ids or []),
            'add_sign': add_sign,
            'record_name': record_name,
        })
        attachments = attachments or []
        attachment_ids = attachment_ids or []
        attachement_values = self._message_post_process_attachments(attachments, attachment_ids, values)
        values.update(attachement_values) 
        message_id = self._message_create(values)
        return message_id
