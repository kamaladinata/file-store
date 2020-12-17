# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class DevEmployeeInsurance(models.Model):
    _name = 'dev.employee.insurance'
    _description = 'Employee Insurance'

    def insurance_running(self):
        self.state = 'running'

    def insurance_expired(self):
        self.state = 'expired'

    def back_to_draft(self):
        self.state = 'draft'

    name = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    insurance_type_id = fields.Many2one('dev.employee.insurance.type', string='Insurance Type')
    employee_company_id = fields.Many2one('res.company', string='Company')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    amount = fields.Float(string='Amount')
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'),
                                                         ('running', 'Running'),
                                                         ('expired', 'Expired')], default='draft')
    description = fields.Text(string='Description')

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
