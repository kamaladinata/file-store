# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Employee Insurance',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        This Module add below functionality into odoo

        1.Employee Insurance\n

Odoo employee Insurance
Employee Insurance
odoo Insurance Management
Odoo Insurance Type
Odoo employee Insurance Management
Odoo employee Insurance Type
Employee Insurance Type
Employee Insurance Management

    """,
    'summary': 'Odoo app Employee Insurance to manage Employee Insurance',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/data_employee_insurance.xml',
        'views/main_menu_view.xml',
        'views/insurance_type_view.xml',
        'views/employee_insurance_view.xml',
        'views/employee_view.xml',
        'report/employee_insurance_pdf_template.xml',
        'report/employee_insurance_pdf_menu.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':10.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
