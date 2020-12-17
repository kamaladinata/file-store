# -*- coding: utf-8 -*-
{
    "name": "Task Check List and Approval Process",
    "version": "13.0.2.0.1",
    "category": "Project",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/13.0/task-check-list-and-approval-process-423",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "project","ja_task_overview"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/project_task_type.xml",
        "views/project_task_lifecycle.xml",
        "views/project_task.xml",
        "views/check_list.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure required jobs are carefully done on this task stage",
    "description": """

For the full details look at static/description/index.html

* Features * 

- Stage-specific checklists

- All required actions are ensured to be done

- Multiple approval roles

- Approval history is kept for managerial control
 
* Extra Notes *


    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
    "live_test_url": "https://odootools.com/my/tickets/newticket?&url_app_id=74&ticket_version=13.0&url_type_id=3",
}