#coding: utf-8

from odoo import fields, models


class project_project(models.Model):
    """
    Overwritting to implement code for tasks auto numbering
    """
    _inherit = "project.project"

    un_reference = fields.Char(string="Code for task numbering:")

    def action_update_numbering(self):
        """
        The method to update numbers of all tasks

        Methods:
         * action_update_numbering of project.task
        """
        for project in self:
            task_ids = self.env["project.task"].search([("project_id", "=", project.id)])
            task_ids.action_update_numbering()
