# -*- coding: utf-8 -*-
{
    "name": "Message / Note Editing",
    "version": "13.0.1.0.2",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/message-note-editing-382",
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
        "views/templates.xml",
        "views/mail_message_view.xml"
    ],
    "qweb": [
        "static/src/xml/message_edit.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to correct accidental mistakes in messages and notes",
    "description": """

For the full details look at static/description/index.html

* Features * 

- Simple Editing

- Universal Use for all Communications

- Safe Updates
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "44.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=37&ticket_version=13.0&url_type_id=3",
}