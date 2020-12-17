# -*- coding: utf-8 -*-
{
    "name": "Message Citing",
    "version": "13.0.1.0.2",
    "category": "Discuss",
    "author": "faOtools",
    "website": "https://faotools.com/apps/13.0/message-citing-458",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail",
        "web_editor"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/view.xml",
        "views/res_config_settings.xml",
        "wizard/mail_compose_message.xml",
        "wizard/cite_message.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to find and cite a message in Odoo email composer",
    "description": """

For the full details look at static/description/index.html

* Features * 

- Quick access to search messages

- Simple search of messages to reference

- Cite in a single click

- Configurable header for referred messages
 
* Extra Notes *



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "22.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=94&ticket_version=13.0&url_type_id=3",
}