# -*- coding: utf-8 -*-
{
    "name": "Periodic Reporting and Reminders",
    "version": "13.0.2.0.1",
    "category": "Extra Tools",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/periodic-reporting-and-reminders-385",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/total_notify.xml",
        "data/mail_template.xml",
        "data/cron.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {
        "python": [
                "xlsxwriter"
        ]
},
    "summary": "The tool to generate and periodically send reports and reminders",
    "description": """

For the full details look at static/description/index.html

* Features * 

- Any Odoo documents' reporting

- Configurable statistic and appearance

- Filtering and periods for analysis

- Flexible recurrence

- Aggregated figures

- Reminder for any Odoo partner

- Periodic reporting manager
 
* Extra Notes *

- Reminder view features

- How to limit documents by relative periods

- How to filter documents under analysis

- Which periodicity I may apply

- User rights peculiarities

- Look at popular use cases


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "172.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=6&ticket_version=13.0&url_type_id=3",
}