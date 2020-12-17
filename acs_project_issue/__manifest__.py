# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': 'Issue Tracking',
    'version': '1.0.1',
    'category': 'Project',
    'sequence': 1,
    "author": "Almighty Consulting Solutions Pvt. Ltd., Odoo S.A.",
    'support': 'info@almightycs.com',
    'summary': 'Support, Bug Tracker, Helpdesk',
    'description': """
Track Issues/Bugs Management for Projects
=========================================
This application allows you to manage the issues you might face in a project like bugs in a system, client complaints or material breakdowns.

It allows the manager to quickly check the issues, assign them and decide on their status quickly as they evolve.
project issue issue management

Suivi des problèmes / gestion des bogues pour les projets
========================================
Cette application vous permet de gérer les problèmes que vous pourriez rencontrer dans un projet, tels que des bugs dans un système, des plaintes de clients ou des pannes matérielles.

Il permet au responsable de vérifier rapidement les problèmes, de les attribuer et de décider de leur statut rapidement au fur et à mesure de leur évolution.
gestion des problèmes de projet


Verfolgen Sie Probleme / Fehler-Management für Projekte
==========================================
Mit dieser Anwendung können Sie Probleme verwalten, mit denen Sie möglicherweise in einem Projekt konfrontiert sind, z. B. Systemfehler, Kundenbeschwerden oder Materialausfälle.

Dadurch kann der Manager die Probleme schnell überprüfen, sie zuweisen und über ihren Status schnell entscheiden, wenn sie sich entwickeln.
Projekt-Issue-Management

Seguimiento de problemas / Gestión de errores para proyectos
=========================================
Esta aplicación le permite administrar los problemas que podría enfrentar en un proyecto, como errores en un sistema, quejas de clientes o averías de materiales.

Le permite al administrador revisar rápidamente los problemas, asignarlos y decidir sobre su estado rápidamente a medida que evolucionan.
problema de proyecto gestión de problemas


Problemen met fouten / bugs beheren voor projecten
=========================================
Met deze applicatie kunt u de problemen beheren die u tegenkomt in een project, zoals bugs in een systeem, klachten van klanten of defecten van materiaal.

Hiermee kan de manager de problemen snel controleren, toewijzen en snel hun status bepalen als ze zich ontwikkelen.
probleem met projectproblematiek

    """,
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': [
        'project', 'hr_timesheet'
    ],
    'data': [
        'data/data.xml',
        'data/mail_message_subtype_data.xml',
        'report/project_issue_report_views.xml',
        'security/project_issue_security.xml',
        'security/ir.model.access.csv',
        'views/project_issue_views.xml',
        'views/account_analytic_account_views.xml',
        'views/project_project_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': ['data/project_issue_demo.xml'],
    'images': [
        'static/description/project_issue_cover_almightycs_odoo.jpg',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'price': 55,
    'currency': 'EUR',
}
