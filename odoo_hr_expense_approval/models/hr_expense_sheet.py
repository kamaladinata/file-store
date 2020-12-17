# -*- coding: utf-8 -*-

from odoo import fields, models, api , _ #odoo13
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError #odoo13


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    department_manager_probc_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        copy=True,
    )

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.department_manager_probc_id = self.sudo().employee_id.expense_dept_manager_id
        else:
            self.department_manager_probc_id = False

    @api.model
    def create(self, values):
        res = super(HrExpense, self).create(values)
        expense_group = self.env.ref('hr_expense.group_hr_expense_team_approver')
        dept_manager = res.department_manager_probc_id
        if dept_manager.sudo().user_id not in expense_group.users:
            raise UserError(_("Department Manager does not have access right to approve Expense!"))
        return res

    def write(self, values):
        dept_manager = self.department_manager_probc_id
        expense_group = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if dept_manager.sudo().user_id not in expense_group.users:
            raise UserError(_("Department Manager does not have access right to approve Expense!"))
        return super(HrExpense, self).write(values)

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection([
            ('draft', 'Draft'), #odoo13
            ('submit', 'Submitted'),
            ('department_app', 'Approved By Department'),
            ('approve', 'Approved'),
            ('finance_app', 'Approved By Finance'),
            ('post', 'Posted'),
            ('done', 'Paid'),
            ('cancel', 'Refused')],
    )
    department_manager_id = fields.Many2one(
        'hr.employee',
        'Department Manager',
    )

    def approve_department_expense_sheets(self):
        for rec in self:
            rec.state = 'department_app'

    def approve_finance_expense_sheets(self):
        for rec in self:
            rec.state = 'finance_app'

    def action_sheet_move_create(self):
        if any(sheet.state != 'finance_app' for sheet in self):
            raise UserError(_("You can only generate accounting entry for Finanace Approval expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.action_move_create()

        if not self.accounting_date:
            self.accounting_date = self.account_move_id.date

        if self.payment_mode == 'own_account' and expense_line_ids:
            self.write({'state': 'post'})
        else:
            self.write({'state': 'done'})
        self.activity_update()
        return res

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.department_manager_id = self.sudo().employee_id.expense_dept_manager_id
        else:
            self.department_manager_id = False

    @api.model
    def create(self, values):
        res = super(HrExpenseSheet, self).create(values)
        expense_group = self.env.ref('hr_expense.group_hr_expense_team_approver')
        dept_manager = res.department_manager_id
        if dept_manager.sudo().user_id not in expense_group.users:
            raise UserError(_("Department Manager does not have access right to approve Expense!"))
        return res

    def write(self, values):
        dept_manager = self.department_manager_id
        expense_group = self.env.ref('hr_expense.group_hr_expense_team_approver')
        if dept_manager.sudo().user_id not in expense_group.users:
            raise UserError(_("Department Manager does not have access right to approve Expense!"))
        return super(HrExpenseSheet, self).write(values)

    def _compute_can_reset(self):
        # Override current method to fix issue department manager
        is_expense_user = self.user_has_groups('hr_expense.group_hr_expense_team_approver')
        for sheet in self:
            sheet.can_reset = is_expense_user
