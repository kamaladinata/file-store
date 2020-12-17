# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################


{
    "name" : "All in one Product Bundle Pack(Sale/POS/Website)",
    "version" : "11.0.0.3",
    "category" : "Sales",
    "depends" : ['base','sale_management','point_of_sale','website_sale','purchase'],
    "author": "BrowseInfo",
    'summary': 'This apps helps to manage product bundle',
    "price": 89,
    "currency": 'EUR',
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps.    
    Purpose :- 
    
Product bundling is offering several products for sale as one combined product. It is a common feature in many imperfectly competitive product markets where price plays important roles, using these module you can act set competitive price for same or different products and variants to increase your sales graph.
        -Point Of sale Product Bundle
        -POS product bundle
        -Point of sale Pack
        -POS product pack
        -Point of sale product pack
        -Custom pack on POS
        -Combined product on POS
        -Product Pack, Custom Combo Product, Bundle Product. Customized product, Group product.Custom product bundle. Custom Product Pack.
         -Pack Price, Bundle price, Bundle Discount, Bundle Offer.
	This module is use to create Product Bundle,Product Pack, Bundle Pack of Product, Combined Product pack.
    -Product Pack, Custom Combo Product, Bundle Product. Customized product, Group product.Custom product bundle. Custom Product Pack.
    -Pack Price, Bundle price, Bundle Discount, Bundle Offer.
    -Website Product Bundle Pack, Website Product Pack, eCommerce Product bundle. All Product bundle feature, All IN one product pack 
    """,
    "website" : "www.browseinfo.in",
    "data": [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/template.xml',
        'views/custom_pos_view.xml',
        'views/product_pack_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_product_bundle_pack.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
