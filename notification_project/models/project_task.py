# -*- coding: utf-8 -*-

import logging

from datetime import date

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class project_task(models.Model):
    """
    Override to introduce cron to send notifications by project tasks
    """
    _inherit = 'project.task'

    @api.depends("user_id")
    def _compute_url_user(self):
        """
        Compute method for url_user

        Methods:
         * _get_signup_url_for_action of res.partner
        """
        for task in self.sudo():
            url_user = False
            if task.user_id:
                url_user = task.user_id.partner_id.with_context(signup_valid=True)._get_signup_url_for_action(
                    view_type="form",
                    model=self._name,
                    res_id=task.id,
                )[task.user_id.partner_id.id]
                url_user = url_user.replace('res_id', 'id')
            task.url_user = url_user


    url_user = fields.Char(
        compute=_compute_url_user,
        store=True,
    )

    @api.model
    def cron_notify(self):
        """
        The method to notify tasks responsibles about overdue and today tasks

        Methods:
         * render_template of mail.template
         * send_email of ir.mail_server
         * build_email of ir.mail_server

        Extra info:
         * Message is not attached to any Odoo object on purpose. There is no sense in it
        """
        context = self.env.context.copy()
        context.update({
            'date': date,
            'company': self.env.user.company_id.name,
            'only_user_sign': True,
        })
        stage_ids = self.env['project.task.type'].search([('is_notify', '=', True)])
        today_date = fields.Date.today()
        task_ids = self.env["project.task"].search([
            ('date_deadline', '<=', today_date),
            ('stage_id', 'in', stage_ids.ids),
            ('user_id', '!=', False)
        ])
        user_ids = task_ids.mapped("user_id")
        for user in user_ids:
            try:
                user_task_ids = task_ids.filtered(lambda lead: lead.user_id == user)
                context.update({"task_ids": user_task_ids})
                # Ugly hack to force Odoo translate template
                template = self.with_context(lang=user.partner_id.lang).env.ref(
                    'notification_project.project_task_notification_template'
                )
                body_html = template.with_context(context)._render_template(
                    template.body_html,
                    'res.users',
                    user.id,
                )
                subject = template.with_context(context).subject
                mail_server = self.env['ir.mail_server']
                message = mail_server.build_email(
                    email_from=self.env.user.email,
                    subject=subject,
                    body=body_html,
                    subtype='html',
                    email_to=[user.partner_id.email],
                )
                mail_server.send_email(message)
            except Exception as e:
                _logger.error("Daily reminder is not sent to user {}. Reason: {}".format(user.name, e))
