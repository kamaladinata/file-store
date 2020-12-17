# -*- coding: utf-8 -*-
{
    "name": "Odoo Email Suite",
    "version": "13.0.1.0.1",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/odoo-email-suite-419",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "internal_thread",
        "compoze_no_auto_subscribe",
        "mail_manual_routing",
        "message_delete",
        "message_edit"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "Set of apps to simplify and improve Odoo messaging experience",
    "description": """

For the full details look at static/description/index.html

* Features * 

- No auto following and no sudden spam

- Editing and deleting messages

- No incoming messages are lost

- Private and confidential communication
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "0.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=43&ticket_version=13.0&url_type_id=3",
}