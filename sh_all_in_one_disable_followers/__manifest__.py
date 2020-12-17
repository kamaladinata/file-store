# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "All in One Disable Followers | Sale Order Disable Followers | Purchase Order Disable Followers | Invoice Disable Followers",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "summary": "Hide Followers In Sale Order, Remove Sales Followers, Disable account Auto Add Followers, Quotation Invisible Followers Module, Partner Not Add In Follower App, Customer Not Add In Follower, Vendor Not Add In Followers In Bill Odoo",
    "description": """
Generally in the odoo automatically partners(customers, vendors, contacts) added as the followers. so our module restricts that.This module disables the partners automatically added as followers. This module includes,

1) Confirmation Quotation: When you confirm the quotation the partners not added as the followers.

2) Validate Invoice/Bill/Credit Note/Debit Note: When you validate the invoice/bill/credit note/debit note the partners not added as the followers.

3) Send By Email: When you press send by email button in the sale order/quotation, purchase order/request for quotation & invoice/credit note the partners not added as the followers.

 All In One Disable Followers Odoo
 Invisible Followers In Sale Order Module, Partner Not Add In Follower, Customer Not Add In Follower, Hide Followers In Quotation, Remove Sales Followers, Disable Auto Add Followers In Invoice, Vendor Not Add In Followers Odoo
 Hide Followers In Sale Order, Remove Sales Followers, Disable Invoice Auto Add Followers, Quotation Invisible Followers Module, Partner Not Add In Follower App, Customer Not Add In Follower, Vendor Not Add In Followers In Bill Odoo""",
    "version": "13.0.3",
    "depends": ["base",
                "sale_management",
                "stock",
                "account",
                "purchase",
                "mail"
                ],
    "application": True,
    "data": [
        
        'views/res_config_setting.xml',
        
            ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/wlDsTifXeEk",
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR" 
}
