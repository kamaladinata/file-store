#coding: utf-8

from odoo import fields, models

class ProjectTaskLifecycle(models.Model):
    """ Add checklist to task lifecycle """
    _inherit = "project.task.lifecycle"

    checklist_ids = fields.One2many('check.list', 'lifecycle_id', string='Checklists')