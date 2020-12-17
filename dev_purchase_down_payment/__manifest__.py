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
    'name': 'Purchase Advance Payment',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Purchases',
    'description':
        """
        This Module add below functionality into odoo

        1.Make Advance payment of purchase order\n

    Odoo vendor payment 
    Odoo vendor Advance payment 
    Odoo supplier Advance payment 
    Odoo vendor purchase Advance payment 
    Odoo supplier purchase Advance payment 

    """,
    'summary': 'odoo app allow to generate purchase advance payment (Fixed/percentage) On purchase order',
    'depends': ['purchase', 'account'],
    'data': [
        'views/res_config_settings_views.xml',
        'wizard/purchase_down_payment_views.xml',
        'views/purchase_views.xml',
        'views/account_invoice_views.xml',
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
    'price':49.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
