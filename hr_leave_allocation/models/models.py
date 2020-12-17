# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class BulkLeaveAllocation(models.Model):
    _name = 'bulk.leave.allocation'
    _inherit = ['mail.thread']
    _description = 'Bulk Leave Allocation'

    @api.depends('employee_ids')
    def _get_total_leave_allocation(self):
        for obj in self:
            obj.total_leaves_to_allocate = len(obj.employee_ids)

    @api.depends('leaves_ids')
    def _get_total_allocated(self):
        for obj in self:
            obj.total_allocated = len(obj.leaves_ids)

    @api.depends('total_leaves_to_allocate','total_allocated')
    def _is_allocted(self):
        for obj in self:
            if obj.total_leaves_to_allocate - obj.total_allocated > 0:
                obj.is_allocated = True
            else:
                obj.is_allocated = False

    name = fields.Char(
        'Description', required=True, tracking=True,
    )
    holiday_status_id = fields.Many2one(
        "hr.leave.type", "Leave Type", required=True,
        tracking=True,
        )
    employee_ids = fields.Many2many(
        'hr.employee', "bulk_leave", "emp_id", "leaves_id",
        string="Employees", required=True)
    number_of_days_temp = fields.Float(
        'Duration', required=True, tracking=True,
    )
    status = fields.Selection(
        [("confirm", "To Approve"), ("validate", "Approved")],
        "Leave Status", default="validate",
        tracking=True,
        )
    leaves_ids = fields.One2many(
        "hr.leave.allocation", 'allocation_id', string="Leaves")
    total_leaves_to_allocate = fields.Integer(
        string="Total Leaves(To Allocate)",
        compute="_get_total_leave_allocation", store=True)
    total_allocated = fields.Integer(
        string="Total Allocated",  compute="_get_total_allocated", store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('allocate', 'Allocated'),
            ('cancel', 'Cancelled')], string="Status",
        default='draft',
        tracking=True,
            )
    is_allocated = fields.Boolean(string="Is Allocated", compute="_is_allocted")

    def allocate_leaves(self):
        for obj in self:
            obj.state = 'allocate'
            obj.allocate_employee_leaves()
        return True

    def allocate_employee_leaves(self):
        for obj in self:
            if obj.state != 'cancel':
                leave_vals = {
                    "name": self.name,
                    "holiday_status_id": self.holiday_status_id.id,
                    "holiday_type": "employee",
                    "number_of_days": self.number_of_days_temp,
                    'allocation_id': obj.id
                }
                employee_list = obj.employee_ids.ids
                if obj.leaves_ids:
                    for leave in obj.leaves_ids:
                        if leave.employee_id.id in employee_list:
                            employee_list.remove(leave.employee_id.id)
                obj.create_leave(employee_list, leave_vals)
        return True

    def create_leave(self, employee_ids, leave_vals):
        self.ensure_one()
        for employee in employee_ids:
            leave_vals["employee_id"] = employee
            leave_obj = self.env["hr.leave.allocation"].create(leave_vals)
            if self.status == "validate":
                leave_obj.action_validate()
                self._cr.commit()
        return True

    def cancel_leaves(self):
        for obj in self:
            if obj.state == 'draft':
                obj.state = 'cancel'

    @api.model
    def create(self, vals):
        if not len(vals.get('employee_ids')[0][2]):
            raise UserError(_('At least one employee required.'))
        return super(BulkLeaveAllocation, self).create(vals)

class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    allocation_id = fields.Many2one(
        "bulk.leave.allocation", string="Allocation Request")
