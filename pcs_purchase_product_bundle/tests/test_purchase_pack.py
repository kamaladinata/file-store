# -*- coding: utf-8 -*-
from odoo.addons.stock.tests.common2 import TestStockCommon
from datetime import datetime, timedelta
from odoo.tests import Form, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged('-at_install', 'post_install')
class TestPurchasePack(TestStockCommon):


    def setUp(self):
        res = super(TestPurchasePack, self).setUp()

        self.vendor = self.env['res.partner'].create({
            'name': 'Supplier',
            'email': 'supplier.serv@supercompany.com',
        })

        Product = self.env['product.product']
        self.product_0 = Product.create({
            'name': 'iPhone 6',
            'type': 'product',
            'lst_price': 100,
            'standard_price': 80,
            'purchase_method': 'purchase',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})
        self.product_1 = Product.create({
            'name': 'iMac',
            'type': 'product',
            'lst_price': 200,
            'standard_price': 180,
            'purchase_method': 'purchase',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})
        self.product_2 = Product.create({
            'name': 'iPod',
            'type': 'product',
            'lst_price': 50,
            'standard_price': 40,
            'purchase_method': 'purchase',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})
        
        self.product_3 = Product.create({
            'name': 'Samsung S20',
            'type': 'product',
            'lst_price': 1,
            'standard_price': 0,
            'purchase_method': 'purchase',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id})

        self.product_apple_bundle = self.env['product.template'].create({
            'name': 'Apple',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'is_pack': True,
            'is_calpack_price': True,
            'purchase_method': 'purchase',
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

        self.total_price = self.total_cost = self.count_item_pack = 0
        for pack in self.product_apple_bundle.product_pack_ids:
            self.total_price += pack.qty_uom *pack.lst_price
            self.total_cost += pack.qty_uom *pack.standard_price
            self.count_item_pack += pack.qty_uom
        self.product_apple_bundle.write({'standard_price': self.total_cost, 'list_price': self.total_price})
        self.product_bundle_id = self.product_apple_bundle.product_variant_ids[0]

        self.order_vals = {
            'partner_id': self.vendor.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_bundle_id.name,
                    'product_id':self.product_bundle_id.id,
                    'product_qty': 1,
                    'product_uom': self.product_bundle_id.uom_po_id.id,
                    'price_unit': self.product_bundle_id.standard_price,
                    'date_planned': datetime.today().replace(hour=9).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': self.product_3.name,
                    'product_id': self.product_3.id,
                    'product_qty': 1,
                    'product_uom': self.product_3.uom_po_id.id,
                    'price_unit': 250.0,
                    'date_planned': datetime.today().replace(hour=9).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }
        group_purchase_user = self.env.ref('purchase.group_purchase_user')
        group_employee = self.env.ref('base.group_user')
        group_partner_manager = self.env.ref('base.group_partner_manager')
        group_account_invoice = self.env.ref('account.group_account_invoice')

        self.purchase_user = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Purchase user',
            'login': 'purchaseUser',
            'email': 'pu@odoo.com',
            'groups_id': [(6, 0, [group_account_invoice.id, group_purchase_user.id, group_employee.id, group_partner_manager.id])],
        })

        return res
    
    def test_bundle_is_product_pack(self):
        """ Ensure the product is product bundle or not, check field is_pack and product_pack_ids not null """
        template = self.product_apple_bundle
        product_pack_ids = template.product_pack_ids
        self.assertTrue(template.is_pack, 'Product template is a bundle pack')
        self.assertTrue(len(product_pack_ids) != 0, 'Product: a product bundle should have product pack')
        self.assertEqual(len(product_pack_ids), 3, 'Product: a product bundle should have product pack')

    def test_bundle_not_have_variants(self):
        """ Ensure the product bundle doesn't have product variants """
        template = self.product_apple_bundle
        attribute_line_ids = template.attribute_line_ids
        self.assertTrue(template.is_pack, "Product bundle is doesn't have variants")
        self.assertEqual(len(attribute_line_ids), 0, 'Product: a product bundle should not have product variant')

    def test_product_bundle_price_calculation(self):
        """ Ensure the calculation price and cost in product bundle is correct """
        template = self.product_apple_bundle
        template.write({'is_calpack_price': False})
        template.write({'is_calpack_price': True})
        self.assertEqual(template.list_price, self.total_price, 'Product: a product bundle canculation sale price')
        self.assertEqual(template.standard_price, self.total_cost, 'Product: a product bundle canculation product cost')

    def test_bundle_purchase_method(self):
        """ Ensure the Control Policy products is On ordered quantities """
        template = self.product_apple_bundle
        self.assertEqual(template.purchase_method, 'purchase', 'Product: the Control Policy is On ordered quantities')

    def test_purchase_order_product_bundle(self):
        """ Ensure the process confirm Purchase Order will unpack the product bundle in picking operation """
        self.purchase = self.env['purchase.order'].with_user(self.purchase_user).create(self.order_vals)
        self.assertTrue(self.purchase, 'Purchase: no purchase order created')
        self.assertEqual(self.purchase.invoice_status, 'no', 'Purchase: PO invoice_status should be "Not purchased"')
        self.assertEqual(self.purchase.order_line.mapped('qty_received'), [0.0, 0.0], 'Purchase: no product should be received"')
        self.assertEqual(self.purchase.order_line.mapped('qty_invoiced'), [0.0, 0.0], 'Purchase: no product should be invoiced"')

        self.purchase.button_confirm()
        self.assertEqual(self.purchase.state, 'purchase', 'Purchase: PO state should be "Purchase"')
        self.assertEqual(self.purchase.invoice_status, 'to invoice', 'Purchase: PO invoice_status should be "Waiting Invoices"')

        self.assertEqual(self.purchase.picking_count, 1, 'Purchase: one picking should be created"')
        self.picking = self.purchase.picking_ids[0]
        self.picking.move_line_ids.write({'qty_done': 1.0})
        self.picking.button_validate()

        product_bundle_line = self.purchase.order_line.filtered(lambda l: l.product_id == self.product_bundle_id)
        product_3_line = self.purchase.order_line.filtered(lambda l: l.product_id == self.product_3)
        self.bundle_order_qty = sum(product_bundle_line.mapped('product_uom_qty'))
        self.product_3_order_qty = sum(product_3_line.mapped('product_uom_qty'))
        self.total_bundle_order_qty = self.count_item_pack *self.bundle_order_qty

        self.assertEqual(self.bundle_order_qty, 1, 'Purchase: product bundle ordered quantity')
        self.assertEqual(self.total_bundle_order_qty, 3, 'Purchase: product bundle total quantity')
        self.assertEqual(self.product_3_order_qty, 1, 'Purchase: product Samsung S20 ordered quantity')
        self.assertEqual(product_bundle_line.mapped('qty_received'), [self.total_bundle_order_qty], 'Purchase: the product bundle should be received"')
        self.assertEqual(product_3_line.mapped('qty_received'), [self.product_3_order_qty], 'Purchase: the product samsung S20 should be received"')
        
        action = self.purchase.with_user(self.purchase_user).action_view_invoice()
        invoice_form = Form(self.env['account.move'].with_user(self.purchase_user).with_context(
            action['context']
        ))
        invoice_form.partner_id = self.vendor
        invoice_form.purchase_id = self.purchase
        self.bill = invoice_form.save()

        # Control Policy products is On ordered quantities
        # self.bundle_order_qty = 1
        # self.product_3_order_qty = 1
        self.assertEqual(self.purchase.order_line.mapped('qty_invoiced'), [1, 1], 'Purchase: all products should be invoiced based on ordered quantity"')
