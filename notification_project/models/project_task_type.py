# -*- coding: utf-8 -*-

from odoo import fields, models


class project_task_type(models.Model):
    """
    Override to add setting of which tasks should be notified
    """
    _inherit = 'project.task.type'

    is_notify = fields.Boolean(
        "Send notification",
        help="""Tasks on this stage would be included in daily reminders
        """,
        default=False,
    )
