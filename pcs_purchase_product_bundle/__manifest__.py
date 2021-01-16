# -*- coding: utf-8 -*-
{
    'name': 'Purchase Product Bundle Pack',
    'version': '14.0.0',
    'category': 'Product',
    'author': 'Portcities Ltd.',
    'website': 'http://www.portcities.net',
    'summary': 'Feature Purchase with Product Bundle Pack',
    'description': """
        v 1.0
        author : Kamal \n
        * Add feature product bundle \n
        * Able to purchase order with the product bundle pack
   
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
