odoo.define('movie_booking_system.cart', function (require) {
    'use strict';
    
    var core = require('web.core');
    var config = require('web.config');
    var concurrency = require('web.concurrency');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    var wSaleUtils = require('website_sale.utils');
    require("web.zoomodoo");
    
    var qweb = core.qweb;
    
    publicWidget.registry.Cart = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);

            // page shop/cart
            $('#o_cart_summary').removeClass('col-xl-4')
            $('.oe_cart').removeClass('col-xl-8')
            $('.mb32.d-xl-inline-block').attr('style', 'display: none !important');
            $('hr.d-xl-block').attr('style', 'display: none !important');
            $('h4.d-xl-block').attr('style', 'display: none !important');
            // $('.text-xl-right').removeClass('text-xl-right')
            $('.d-xl-none').removeClass('d-xl-none')
            $('.d-xl-inline-block:gt(0)').attr('style', 'display: none !important');
            $('.d-xl-inline-block:gt(1)').attr('style', 'display: none !important');

            // page shop/payment
            $('.toggle_summary').attr('style', 'display: unset !important');
            $('.toggle_summary_div').attr('style', 'max-width: 100% !important');
            $('.toggle_summary_div').removeClass('d-xl-block');
            $('.toggle_summary').parent().removeClass('p-xl-0')
            $('.toggle_summary').parent().parent().parent().removeClass('col-xl-auto')
            $('.toggle_summary').parent().parent().parent().removeClass('order-xl-2')

            $('.oe_cart').parent().removeClass('col-xl')
            $('.card').parent().removeClass('col-xl-auto')
            $('#cart_products').parent().css('max-width','none')
            return def;
        },
    });
    });