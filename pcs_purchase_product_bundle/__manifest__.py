# -*- coding: utf-8 -*-
{
    'name': 'Purchase Product Bundle Pack',
    'version': '13.0.1',
    'category': 'Product',
    'author': 'Portcities Ltd.',
    'website': 'http://www.portcities.net',
    'summary': 'Combine two or more products together in order to create a bundle product.',
    'description': """
        v 1.0
        author : Kamal \n
        * This module is use to create Product Bundle Pack \n
        * Which is to combine two or more products together in order to create a bundle product \n
        * Custom purchase order to unpack product bundle in detail picking operation
   
    """,
    'depends': ['purchase_stock'],
    'data':[
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/product_pack_views.xml',
    ],
    'sequence': 1,
    'installable': True,
    'application' : True,
    'auto_install' : False,
    'images': ['static/description/icon.png'],
}
