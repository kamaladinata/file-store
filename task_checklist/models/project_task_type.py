#coding: utf-8

from odoo import fields, models

class project_task_type(models.Model):
    """
    Add checklist to task stages
    """
    _inherit = "project.task.type"

    default_check_list_ids = fields.One2many(
        "check.list",
        "project_task_type_id",
        string="Check List",
    )
    no_need_for_checklist = fields.Boolean(
        string="No need for checklist",
        help="If selected, when you move a task TO this stage no checklist is required (e.g. for 'Cancelled')"
    )
