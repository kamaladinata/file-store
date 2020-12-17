# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoice Tripple Approval Process',
    'version': '11.0.0.0',
    'category': 'Accounting',
    'summary': 'This app allow your workflow on invoice for tripple approval levels based on configuration of amounts and limiation of approval.',
    'description': """ 
    customer invoice Double Validation,
    customer invoice Double approval workflow
    customer invoice Approval workflow
    customer invoice validation workflow
    customer invoice double validation
    customer invoice approval workflow
    customer invoice two step approval
    customer invoice two step validation
    double validation on invoices
    approval workflow on invoices
    Validation process on invoices
    Double validation on invoices
    Confirm invoice approval

    double validation on customer invoices
    approval workflow on customer invoices
    Validation process on customer invoices
    Double validation on customer invoices
    Confirm  customerinvoice approval

    vendor bill Double Validation,
    vendor bill Double approval workflow
    vendor bill Approval workflow
    vendor bill validation workflow
    vendor bill double validation
    vendor bill approval workflow
    vendor bill two step approval
    vendor bill two step validation
    double validation on vendor bills
    approval workflow on vendor bills
    Validation process on vendor bills
    Double validation on vendor bills
    Confirm vendor bill approval

    vendor bills Double Validation,
    vendor bills Double approval workflow
    vendor bills Approval workflow
    vendor bills validation workflow
    vendor bills double validation
    vendor bills approval workflow
    vendor bills two step approval
    vendor bills two step validation

    customer invoice Tripple Validation,
    customer invoice Tripple approval workflow
    customer invoice Tripple workflow
    customer invoice Tripple validation
    customer invoice Tripple approval workflow
    customer invoice three step approval
    customer invoice three step validation
    Tripple validation on invoice
    tripple validation on invoice
    three Confirm customer invoice approval   


    vendor bill Tripple Validation,
    vendor bill Tripple approval workflow
    vendor bill Approval workflow
    vendor bill validation workflow
    vendor bill Tripple validation
    vendor bill approval workflow
    vendor bill three step approval
    vendor bill three step validation
    Tripple validation on vendor bills
    approval workflow on vendor bills
    Validation process on vendor bills
    Tripple validation on vendor bills
    Confirm vendor bill approval

    vendor bills Tripple Validation,
    vendor bills Tripple approval workflow
    vendor bills Approval workflow
    vendor bills validation workflow
    vendor bills Tripple validation
    vendor bills approval workflow
    vendor bills three step approval
    vendor bills three step validation

    Invoice double approval process  helps you to set limit on customer and supplier invoices, it restricts users from validating invoices if total exceeds pre-defined limits and allows to invoice tripple approval.  """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','bi_invoice_double_approval'],
    'data': [
            'security/invoice_groups.xml',
            'views/inherited_res_config_setting_view.xml',
            'views/inherited_account_invoice_view.xml'
            ],
    'demo': [],
    'price': 20,
    'currency': "EUR",
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
}
