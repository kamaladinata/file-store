# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """
    Overwrite to pass to the session whether a user in project user
    """
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        result.update(show_tasks_search=request.env.user.has_group("project.group_project_user"),)
        return result
