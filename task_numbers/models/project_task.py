#coding: utf-8

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class project_task(models.Model):
    """
    Overwritting to implement tasks auto numbering
    """
    _inherit = "project.task"

    @api.depends("project_id.un_reference", "un_reference_short")
    def _compute_un_reference(self):
        """
        Compute method for un_reference
        """
        ICPSudo = self.env['ir.config_parameter'].sudo()
        enable_pr_code = safe_eval(ICPSudo.get_param('enable_project_code_task_number', "False"))
        for task in self:
            if enable_pr_code and task.project_id.un_reference:
                task.un_reference = "{}/{}".format(task.project_id.un_reference, task.un_reference_short)
            else:
                task.un_reference = task.un_reference_short


    un_reference = fields.Char(
        string="Reference Number",
        compute=_compute_un_reference,
        store=True,
        compute_sudo=True,
    )
    un_reference_short = fields.Char(string="Short Reference Number")

    @api.model
    def create(self, vals):
        """
        Re-write to assign un_reference
        """
        vals["un_reference_short"] = self.env['ir.sequence'].sudo().next_by_code('project.task')
        res = super(project_task, self).create(vals)
        return res

    @api.model
    def quick_search(self, args):
        """
        The method to search a task by auto number

        Args:
         * args - dict:
          ** "search" - char to make a search
        """
        search = args.get("search")
        task_ids = self.search([("un_reference", "ilike", search),])
        action_id = False
        if len(task_ids) == 1:
            action_id = self.env.ref("task_numbers.project_task_action_only_form").read()[0]
            action_id['res_id'] = task_ids[0].id
        else:
            action_id = self.env.ref("project.project_task_action_from_partner").read()[0]
            action_id['context'] = {"search_default_un_reference": search}
            action_id["views"] = [(False, 'kanban'), (False, 'list'), (False, 'form')]
        return action_id

    def action_update_numbering(self):
        """
        The method to re-calculate current tasks number
        """
        for task in self:
            task.un_reference_short = self.env['ir.sequence'].sudo().next_by_code('project.task')
