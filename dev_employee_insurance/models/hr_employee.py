# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    insurance_ids = fields.One2many('dev.employee.insurance', 'employee_id', string='Insurance')
    is_own_insurance = fields.Boolean(compute='_compute_insurance_ids')

    @api.depends('insurance_ids')
    def _compute_insurance_ids(self):
        hr_admin = self.env.user.has_group('hr.group_hr_manager')
        for rec in self:
            rec.is_own_insurance = False
            if rec.insurance_ids or hr_admin:
                rec.is_own_insurance = True


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    insurance_ids = fields.One2many('dev.employee.insurance', 'employee_id', string='Insurance')
    is_own_insurance = fields.Boolean(compute='_compute_insurance_ids')

    @api.depends('insurance_ids')
    def _compute_insurance_ids(self):
        hr_admin = self.env.user.has_group('hr.group_hr_manager')
        for rec in self:
            rec.is_own_insurance = False
            if rec.insurance_ids or hr_admin:
                rec.is_own_insurance = True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: