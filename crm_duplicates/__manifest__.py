# -*- coding: utf-8 -*-
{
    "name": "CRM Duplicates Real Time Search",
    "version": "13.0.1.0.3",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/13.0/crm-duplicates-real-time-search-383",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "crm"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/crm_lead.xml",
        "views/res_partner_view.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool for real-time control of customers' and opportunities' duplicates",
    "description": """

For the full details look at static/description/index.html

- If you do not use CRM and searches for the tool only for partners' duplicates, look at the tool &lt;a href='https://apps.odoo.com/apps/modules/13.0/partner_duplicates/'&gt;Contacts Duplicates Real Time Search&lt;/a&gt;

* Features * 

- Real-time duplicates search

- Configurable duplicates' criteria

- Rigid or soft duplicates

- Compatible with Odoo standard features
 
* Extra Notes *

- Performance issues

- How rules work



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "86.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=16&ticket_version=13.0&url_type_id=3",
}