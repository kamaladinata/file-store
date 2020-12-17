#coding: utf-8

from odoo import fields, models

class check_history(models.Model):
    """
    The model to keep approval history
    """
    _name = "check.history"
    _description = "Check List History"

    check_list_id = fields.Many2one("check.list", string="Check Item")
    task_id = fields.Many2one("project.task")
    complete_date = fields.Datetime(
        string="Date",
        default=lambda self: fields.Datetime.now(),
    )
    user_id = fields.Many2one(
        "res.users",
        "User",
        default=lambda self: self.env.user.id,
    )
    done_action = fields.Selection(
        (
            ("done", "Complete"),
            ("reset", "Reset"),
        ),
        string="Action",
        default="done",
    )

    _order = "complete_date DESC,id"

