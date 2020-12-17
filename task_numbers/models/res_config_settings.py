#coding: utf-8

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

PARAMS = [
    ("enable_project_code_task_number", safe_eval, "False"),
]


class res_config_settings(models.TransientModel):
    """
    Overwrite to add numbering settings
    """
    _inherit = 'res.config.settings'

    enable_project_code_task_number = fields.Boolean(string="Project code in task number")

    @api.model
    def get_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        res = super(res_config_settings, self).get_values()
        values = {}
        for field_name, getter, default in PARAMS:
            values[field_name] = getter(str(Config.get_param(field_name, default)))
        res.update(**values)
        return res

    def set_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        super(res_config_settings, self).set_values()
        for field_name, getter, default in PARAMS:
            value = getattr(self, field_name, default)
            Config.set_param(field_name, value)

    def action_update_all_task_numbers(self):
        """
        The method to update numbers of all tasks

        Methods:
         * action_update_numbering of project.task
        """
        task_ids = self.env["project.task"].search([])
        task_ids.action_update_numbering()

    def action_open_ir_task_sequence(self):
        """
        The method to open ir.sequence
        """
        seq_id = self.env["ir.sequence"].search([("code", "=", "project.task")], limit=1)
        if seq_id:
            return {
                "res_id": seq_id.id,
                "name": _("Task Numbering"),
                "type": "ir.actions.act_window",
                "res_model": "ir.sequence",
                "view_mode": "form",
                "target": "new",
            }