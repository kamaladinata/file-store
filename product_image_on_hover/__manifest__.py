# -*- coding: utf-8 -*-
##############################################################################
#
# This module is developed by Portcities Indonesia
# Copyright (C) 2017 Portcities Indonesia (<http://portcities.net>).
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Product Image on Hover',
    'version': '1.0.0',
    'summary': 'Elizabeth Product Image Hover',
    'author': 'PCI',
    'description': """
        - Product Image on Hover
    Features:\n
        1. Hover product image in list view and kanban view
    """,
    'depends': ['web', 'product'],
    'data': [
        "views/inherited_product_kanban_view.xml",
        "views/js_data.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
