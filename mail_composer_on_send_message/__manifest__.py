# -*- coding: utf-8 -*-
{
    "name": "Send Message Composer",
    "version": "13.0.1.0.0",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/send-message-composer-454",
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
        "views/views.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to always open a full composer on the button 'Send a Message'",
    "description": """

For the full details look at static/description/index.html

* Features * 

- The tool works for the button 'Send message' under any Odoo document

- As soon as the button 'Send message' is pressed, the app redirects to the full-featured pop-up email composer window
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "0.0",
    "currency": "EUR",
}