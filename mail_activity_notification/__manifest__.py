# -*- coding: utf-8 -*-
{
    "name": "Activities Daily Reminder",
    "version": "13.0.1.2.3",
    "category": "Discuss",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/activities-daily-reminder-435",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "views/mail_activity_view.xml",
        "data/cron.xml",
        "data/mail_activity_data.xml"
    ],
    "summary": "The tool to notify users of assigned to them activities",
    "description": """

For the full details look at static/description/index.html

- Configure your own single-list reminders for any Odoo records using &lt;a href=&quot;https://apps.odoo.com/apps/modules/13.0/total_notify/&quot;&gt;the tool All-In-One Lists Reminders&lt;/a&gt;

- Some email clients / browser might partially spoil the table appearance

* Features * 

- Single reminder of all topical activities

- Individual list of actions

- Configurable activities reminder
 
* Extra Notes *

- How to change reminders' appearance

- How to change time or frequency of reminders


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=1&ticket_version=13.0&url_type_id=3",
}