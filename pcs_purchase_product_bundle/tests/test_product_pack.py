# -*- coding: utf-8 -*-
from odoo.tests import Form, tagged
from odoo.addons.product.tests.common import TestProductCommon


@tagged('-at_install', 'post_install')
class TestProductPack(TestProductCommon):
    
    def setUp(self):
        res = super(TestProductPack, self).setUp()
        Product = self.env['product.product']
        self.product_0 = Product.create({
            'name': 'iPhone 6',
            'type': 'product',
            'lst_price': 100,
            'standard_price': 80,
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})
        self.product_1 = Product.create({
            'name': 'iMac',
            'type': 'product',
            'lst_price': 200,
            'standard_price': 180,
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})
        self.product_2 = Product.create({
            'name': 'iPod',
            'type': 'product',
            'lst_price': 50,
            'standard_price': 40,
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})

        self.product_apple_bundle = self.env['product.template'].create({
            'name': 'Apple',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'is_pack': True,
            'is_calpack_price': True,
            'product_pack_ids': [(0, 0, {
                'product_id': self.product_0.id,
                'name': self.product_0.name,
                'qty_uom': 1,
                'lst_price': self.product_0.lst_price,
                'standard_price': self.product_0.standard_price,
            }), (0, 0, {
                'product_id': self.product_1.id,
                'name': self.product_1.name,
                'qty_uom': 1,
                'lst_price': self.product_1.lst_price,
                'standard_price': self.product_1.standard_price,
            }),(0, 0, {
                'product_id': self.product_2.id,
                'name': self.product_2.name,
                'qty_uom': 1,
                'lst_price': self.product_2.lst_price,
                'standard_price': self.product_2.standard_price,
            })],
            'attribute_line_ids': [],
        })
        self.total_price = self.total_cost = 0
        for pack in self.product_apple_bundle.product_pack_ids:
            self.total_price += pack.qty_uom *pack.lst_price
            self.total_cost += pack.qty_uom *pack.standard_price
        
        self.product_apple_bundle.write({'standard_price': self.total_cost, 'list_price': self.total_price})
        return res

    def test_bundle_is_product_pack(self):
        """ Ensure the product is product bundle or not, check field is_pack and product_pack_ids not null """
        template = self.product_apple_bundle
        product_pack_ids = template.product_pack_ids
        self.assertTrue(template.is_pack, 'Product template is a bundle pack')
        self.assertTrue(len(product_pack_ids) != 0)
        self.assertEqual(len(product_pack_ids), 3)

    def test_bundle_not_have_variants(self):
        """ Ensure the product bundle doesn't have product variants """
        template = self.product_apple_bundle
        attribute_line_ids = template.attribute_line_ids
        self.assertTrue(template.is_pack, "Product bundle is doesn't have variants")
        self.assertEqual(len(attribute_line_ids), 0)

    def test_product_bundle_price_calculation(self):
        """ Ensure the calculation price and cost in product bundle is correct """
        template = self.product_apple_bundle
        template.write({'is_calpack_price': False})
        template.write({'is_calpack_price': True})
        self.assertEqual(template.list_price, self.total_price)
        self.assertEqual(template.standard_price, self.total_cost)    
