# -*- coding: utf-8 -*-
{
    "name": "No Auto Subscription",
    "version": "13.0.1.2.2",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/no-auto-subscription-417",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "wizard/mail_compose_message.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to exclude automatic following for message recipients",
    "description": """

For the full details look at static/description/index.html

* Features * 

- Full control over followers. No accidental spam

- All cases to be confident
 
* Extra Notes *

- Which Odoo work flows should not be cancelled


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "49.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=39&ticket_version=13.0&url_type_id=3",
}