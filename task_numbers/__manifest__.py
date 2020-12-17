# -*- coding: utf-8 -*-
{
    "name": "Task Auto Numbering and Search",
    "version": "13.0.1.0.3",
    "category": "Project",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/task-auto-numbering-and-search-445",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "project"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/project_task.xml",
        "views/project_project.xml",
        "views/res_config_settings.xml",
        "views/project_task_portal.xml",
        "views/view.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to quickly access and simply reference tasks by automatic numbers",
    "description": """

For the full details look at static/description/index.html

* Features * 

- High available task numbers

- Tasks quick referencing

- Various task code parts

- Automatic and unique task numbers

- Re-computing task references
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "25.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=102&ticket_version=13.0&url_type_id=3",
}