# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models
from datetime import datetime


class EmployeeInsurancePDF(models.AbstractModel):
    _name = 'report.dev_employee_insurance.employee_insurance_pdf_template'

    def format_insurance_dates(self, base_date):
        final_date = base_date
        if base_date:
            final_date = datetime.strptime(str(base_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        return final_date

    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.employee.insurance'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.employee.insurance',
            'docs': docs,
            'format_insurance_dates': self.format_insurance_dates
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: