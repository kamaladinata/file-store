# -*- coding: utf-8 -*-
{
    "name": "Lost Messages Routing",
    "version": "13.0.1.2.5",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/lost-messages-routing-418",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "wizard/mail_attach.xml",
        "views/mail_unattached.xml",
        "views/res_config_settings.xml"
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure you do not loose any incoming messages",
    "description": """

For the full details look at static/description/index.html

* Features * 

- No messages are lost

- Simple addressing of lost messages

- Batch messages' routing

- Not only lost messages
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "36.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=32&ticket_version=13.0&url_type_id=3",
}