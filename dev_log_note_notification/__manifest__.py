# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Send Log Note As Email to Followers/Users',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        This Module add below functionality into odoo

        1.It will send notification emails to the users when you Log any Note it Chatter\n

    """,
    'summary': 'Odoo app allow to send Log As Email notification to Followers/Users, Log Note notification, Log Note mail Followers, Log Note users, Log note mail send notification, log note email followers',
    'depends': ['mail'],
    'data': [
        'security/security.xml',
        'views/res_config_settings_view.xml'
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':29.0,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/9lbhOLFzf7U',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
