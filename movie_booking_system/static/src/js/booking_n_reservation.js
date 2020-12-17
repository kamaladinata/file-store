/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* @License       : https://store.webkul.com/license.html */

odoo.define('movie_booking_system.booking_n_reservation', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var publicWidget = require('web.public.widget');
    var session = require('web.session');
    var rpc = require('web.rpc');
    var Days = {
        'sun' : 0,
        'mon' : 1,
        'tue' : 2,
        'wed' : 3,
        'thu' : 4,
        'fri' : 5,
        'sat' : 6,
    }
    
    publicWidget.registry.SeatBook = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        _pollCount: 0,
        init: function(parent, options){
            $('.js_variant_change').click(function(e) {
                var total = 0 + ($(this).data('price_ori') != undefined) ? parseFloat($(this).data('price_ori')) : 0
                $('.js_variant_change:checked').each(function(){
                    var price_extra = ($(this).data('price_extra') != undefined) ? parseFloat($(this).data('price_extra')) : 0
                    total = total + price_extra
                })
                $('.oe_price').text(total.toFixed(2))
            });
            // window.onbeforeunload = closingCode;
            // getCookie = function(name) {
            //     var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
            //     if (match) return match[2];
            // }
            // function closingCode(){
            //     var uuid = getCookie('visitor_uuid')
            //     ajax.jsonRpc("/booking/release", 'call',{
            //         'visitor_uid' : uuid,
            //     })
            //     console.log("clossing ----- ",uuid)
            //     debugger
            //     return null;
            // }
            var res = this._super.apply(this, arguments);
            return res
        },
        start: function() {
            var self = this;
            self.seat_number = []
            this.poll();
            this.event_listener();
            console.log("session --",session)
            // self.startPolling();
            var res = this._super.apply(this, arguments);
            return res
        },
        /* Methods */
        startPolling: function () {
            var timeout = 1000;
            setTimeout(this.poll.bind(this), timeout);
            this._pollCount ++;
        },
        toggle_book_seat: function(seat, booking_modal){
            var self = this;
            var product_id = parseInt(booking_modal.data('res_id'),10);
            
            var booking_date = booking_modal.find('#bk_sel_date').val();
            var booking_slot_id = false
            var book_slot = booking_modal.find('.bk_slot_div.bk_active').attr('data-slot_plans')
            if (book_slot) {
                booking_slot_id = JSON.parse(booking_modal.find('.bk_slot_div.bk_active').attr('data-slot_plans').replace(/'/g, '"').replace(/F/g, 'f'))[0]['id']
            }
            console.log("product_id: ",product_id)
            console.log("check this: ", booking_modal)
            var seat_data = {}
            if (seat.status()== 'available'){
                seat_data  = {
                    'booking_date' : booking_date,
                    'booking_slot_id': booking_slot_id,
                    'seat_id': seat.settings.id,
                    'book': true,
                    'user_id': session.user_id,
                    'product_id': product_id,
                    'line_id': self.line_id,
                }
                self.seat_number.push(seat.settings.id)
            }else if (seat.status() == 'selected'){
                seat_data  = {
                    'booking_date' : booking_date,
                    'booking_slot_id': booking_slot_id,
                    'seat_id': seat.settings.id,
                    'book': false,
                    'user_id': session.user_id,
                    'product_id': product_id,
                    'line_id': self.line_id,
                }
                self.seat_number.splice( self.seat_number.indexOf(seat.settings.id), 1 );
            }
            
            console.log("rpc -------",seat_data)
            // rpc.query({
            //     model: 'seat.book',
            //     method: 'togglebook',
            //     args: [seat_data],
            // })
            function removeA(arr) {
                var what, a = arguments, L = a.length, ax;
                while (L > 1 && arr.length) {
                    what = a[--L];
                    while ((ax= arr.indexOf(what)) !== -1) {
                        arr.splice(ax, 1);
                    }
                }
                return arr;
            }
            ajax.jsonRpc("/booking/reservation/togglebook", 'call', seat_data)
            .then(function(result){
                if ($('#array_bk_data').val()){
                    var bk_data = JSON.parse($('#array_bk_data').val());
                }
                else{
                    var bk_data = [];
                }
                for (var i=0;i<result.length;i++){
                    var book = result[i];
                    if (book.book){
                        bk_data.push(book.id)
                    }else {
                        bk_data = removeA(bk_data, book.id);
                    }
                }
                var res = JSON.stringify(bk_data);
                $('#array_bk_data').val(res);
                $.unblockUI()
            })

            
        },
        event_listener: function(){
            
            console.log("event listener called")
            var self = this;
            var reset_total_price = function(){
                var bk_total_price = $('.modal_shown').closest('#booking_modal').find('.bk_total_price .oe_currency_value');
                bk_total_price.html('0.00');
            }

            var get_w_closed_days = function(w_c_days){
                var data = w_c_days.map(day => Days[day])
                return data
            }
            
            
            
            $('a[href="/shop/checkout?express=1"]').on("click", function(e) {
                e.preventDefault();
                $.blockUI();
                ajax.jsonRpc("/booking/check", 'call')
                .then(function(res){
                    $.unblockUI();
                    if (res.missing) {
                        var bk_modal_err = $('.bk_modal_err');
                        bk_modal_err.html(res.info).show();
                        setTimeout(function() {
                            bk_modal_err.empty().hide()
                        }, 10000);
                    }
                    else {
                        window.location.href = "/shop/checkout?express=1";
                    }

                    
                })
            });
              
            $('.bk_cart_plan').click(function(evnt){
                var appdiv = $(this).prev();
                
                console.log("evnt -------",$(this))
                var bk_loader = $('#bk_n_res_loader');
                var product_id = parseInt(appdiv.data('res_id'),10);
                var line_id = parseInt(appdiv.data('line_id'),10);
                var slot_id_ori = parseInt(appdiv.data('slot_id'),10);
                var combo_id = parseInt(appdiv.data('combo_id'),10);
                var unit_price = parseFloat(appdiv.data('unit_price'));
                console.log("product id -----------",product_id, line_id)
                var redirect = window.location.pathname;
                bk_loader.show();
                ajax.jsonRpc("/booking/reservation/modal", 'call',{
                    'product_id' : product_id,
                    'line_id': line_id,
                    'combo_id':combo_id
                })
                .then(function (modal) {
                    bk_loader.hide();
                    var $modal = $(modal);
                    var mod = $modal.appendTo(appdiv)
                        .modal({
                            backdrop: 'static',
                            keyboard: false
                        })
                        
                        
                        // Booking Date Selection Picker
                        var today = new Date();
                        var date_default = today.getFullYear()+'-'+("0" + (today.getMonth() + 1)).slice(-2)+'-'+("0" + today.getDate()).slice(-2);
                        var date = new Date();
                        var max_booking = parseInt($('.max_booking').text());
                        date.setDate(date.getDate() + max_booking);
                        var end_date = $('#bk_datepicker').data('bk_end_date')
                        var seat_sel = appdiv.find('#array_bk_data').val();
                        if (seat_sel){
                            var seat_sel = JSON.parse(seat_sel);
                        }else{
                            var seat_sel = [];
                        }
                        console.log("seat selected ======",seat_sel)
                        var end_date_date = new Date(end_date)
                        if (date <= end_date_date){
                            end_date = date;
                        }
                        appdiv.find('.guest').addClass('d-none');
                        appdiv.find('.book_now').addClass('d-none');
                        appdiv.find('.update_book').removeClass('d-none');
                        var disabledDate = ( $('#bk_datepicker').data('blocked_date') != undefined) ? $('#bk_datepicker').data('blocked_date') : false
                        $(function () {
                            if ($('#bk_datepicker').length > 0){
                                    $('#bk_datepicker').datetimepicker({
                                        format: 'YYYY-MM-DD',
                                        icons: {
                                            date: 'fa fa-calendar',
                                            next: 'fa fa-chevron-right',
                                            previous: 'fa fa-chevron-left',
                                        },
                                        // defaultDate : new Date(),
                                        minDate : $('#bk_datepicker').data('bk_current_date'),
                                        maxDate : end_date,
                                        defaultDate : $('#bk_datepicker').data('bk_default_date'),
                                        daysOfWeekDisabled : get_w_closed_days($('#bk_datepicker').data('w_c_days')),
                                        disabledDates: [moment(disabledDate,'YYYY-MM-DD')],
                                    });
                                }
                            });
                        

                        $('#bk_datepicker').on("change.datetimepicker", function (e) {
                        // $('#bk_datepicker').on("dp.change", function (e) {
                            var date = new Date(e.date);
                            var o_date = new Date(e.oldDate);
                            function GetFormate(num){
                                if(num<10)
                                {
                                    return '0'+num;
                                }
                                return num
                            }
                            function GetFormattedDate(date) {
                                var month = GetFormate(date .getMonth() + 1);
                                var day = GetFormate(date .getDate());
                                var year = date .getFullYear();
                                return day + "/" + month + "/" + year;
                            }
                            if(GetFormattedDate(date) != GetFormattedDate(o_date)){
                                bk_loader.show();
                                self.render_seat(appdiv,[],true, seat_sel);
                                ajax.jsonRpc("/booking/reservation/modal/update", 'call',{
                                    'product_id' : product_id,
                                    'new_date' : GetFormattedDate(date),
                                    'user_id': session.user_id,
                                    'line_id': line_id,
                                    'array_data': seat_sel,
                                    'slot_id':slot_id_ori
                                })
                                .then(function (result) {
                                    bk_loader.hide();
                                    if((date.getMonth() != o_date.getMonth()) || (date.getFullYear() != o_date.getFullYear())){
                                        var date_str = date.toUTCString();
                                        date_str = date_str.split(' ').slice(2,4)
                                        document.getElementById("dsply_bk_date").innerHTML = date_str.join(", ");
                                    }
                                    var bk_slots_main_div = appdiv.find('.bk_slots_main_div');
                                    reset_total_price();
                                    bk_slots_main_div.html(result);
                                    $('.modal_shown').closest('#booking_modal').on('click','.bk_slot_div',function(evnt){
                                        var $this = $(this);
                                        console.log("change slot")
                                        var slot_plans = $this.data('slot_plans');
                                        var booking_modal = $('.modal_shown').closest('#booking_modal');
                                        var bk_loader = $('#bk_n_res_loader');
                                        var time_slot_id = parseInt($this.data('time_slot_id'),10);
                                        var line_id = booking_modal.data('line_id')
                                        if(line_id){
                                            line_id = parseInt(line_id,10);
                                            var slot_id = parseInt($this.data('slot_id'),10);
                                        }
                                        
                                        var model_plans = booking_modal.find('.bk_model_plans');
                                        var seat = booking_modal.find('#array_bk_data').val();
                                        if (seat){
                                            var seat = JSON.parse(seat);
                                        }else{
                                            var seat = [];
                                        }
                                        var bk_modal_slots = booking_modal.find('.bk_modal_slots');
                                        var product_id = parseInt(booking_modal.data('res_id'),10);
                                        var bk_sel_date = $('#bk_sel_date');
                                        bk_loader.show();
                                        self.render_seat(booking_modal, [], true);
                                        ajax.jsonRpc("/booking/reservation/slot/plans", 'call',{
                                            'time_slot_id' : time_slot_id,
                                            'slot_plans' : slot_plans,
                                            'line_id': line_id,
                                            'sel_date' : bk_sel_date.val(),
                                            'product_id' : product_id,
                                            'seat': seat,
                                            'user_id': session.user_id
                                        })
                                        .then(function (result) {
                                            bk_loader.hide();
                                            reset_total_price();
                                            model_plans.html(result);
                                            booking_modal.find('#array_bk_data').val('')
                                            if (line_id){
                                                ajax.jsonRpc("/booking/reservation/cart/update_date", 'call',{
                                                    'product_id': product_id,
                                                    'line_id' : line_id,
                                                    'booking_date': bk_sel_date.val(),
                                                    'slot_id': slot_id
                                                })
                                            }
                                        });
                                        bk_modal_slots.find('.bk_slot_div').not($this).each(function(){
                                            var $this = $(this);
                                            if($this.hasClass('bk_active')){
                                                console.log("bk class removed")
                                                $this.removeClass('bk_active');
                                            }
                                        });
                                        if(!$this.hasClass('bk_active')){
                                            $this.addClass('bk_active');
                                            $('.seat-cont').show()
                                        }
                                    });
                                    var booking_date = appdiv.find('#bk_sel_date').val();
                                    ajax.jsonRpc("/booking/reservation/cart/update_date", 'call',{
                                        'product_id': product_id,
                                        'line_id' : line_id,
                                        'booking_date': booking_date,
                                    })
                                    var slot_id = $('.bk_slot_div.bk_active')
                                    if (slot_id.length == 0){
                                        $('.seat-cont').hide()
                                    }
                                    else{
                                        $('.seat-cont').show()
                                    }

                                    
                                    mod.on('hidden.bs.modal', function () {
                                        var product_id = parseInt(appdiv.data('product_id'),10);
                                        var seat_final = appdiv.find('#array_bk_data').val();
                                        if (seat_final){
                                            var seat_final = JSON.parse(seat_final);
                                        }else{
                                            var seat_final = [];
                                        }
                                        var slot_id = $('.bk_slot_div.bk_active')
                                        if (slot_id.length == 0){
                                            ajax.jsonRpc("/booking/reservation/cart/update", 'call',{
                                                'product_id': product_id,
                                                'add_qty' : 0,
                                                'line_id' : line_id,
                                                'booking_date': booking_date,
                                                'booking_slot_id': slot_id,
                                                'combo_id': combo_id,
                                                'unit_price':unit_price
                                            })
                                            .then(function (result) { 
                                                var cont = $('#cart_products');
                                                var tot = $('#cart_total');
                                                cont[0].innerHTML = result.cart;
                                                tot[0].innerHTML = result.total;
                                                $('.js_cart_summary .d-none:not(".coupon_form")').attr('style', 'display: none !important')
                                                self.event_listener();
                                                if (publicWidget.registry.Loyalty){
                                                    var loyalty = new publicWidget.registry.Loyalty();
                                                    loyalty.event_listener();
                                                }
                                                $.unblockUI();
                                                // location.reload();
                                            })
                                            return
                                        }
                                        console.log("slot id :",slot_id)
                                        var slot_id = JSON.parse($('.bk_slot_div.bk_active').attr('data-slot_plans').replace(/'/g, '"').replace(/F/g, 'f'))[0]['id']
                                        var booking_date = appdiv.find('#bk_sel_date').val()
                                        
                                        $.blockUI();
                                        ajax.jsonRpc("/booking/reservation/cart/update", 'call',{
                                            'product_id': product_id,
                                            'add_qty': 0,
                                            'set_qty': parseInt(appdiv.find('.counter').text()),
                                            'line_id' : line_id,
                                            'seat_ids' : seat_final,
                                            'booking_date': booking_date,
                                            'booking_slot_id': slot_id,
                                            'combo_id': combo_id,
                                            'unit_price':unit_price
                                        })
                                        .then(function (result) { 
                                            var cont = $('#cart_products');
                                            var tot = $('#cart_total');
                                            cont[0].innerHTML = result.cart;
                                            tot[0].innerHTML = result.total;
                                            $('.js_cart_summary .d-none:not(".coupon_form")').attr('style', 'display: none !important')
                                            self.event_listener();
                                            if (publicWidget.registry.Loyalty){
                                                var loyalty = new publicWidget.registry.Loyalty();
                                                loyalty.event_listener();
                                            }
                                            $.unblockUI();
                                            // location.reload();
                                        })
                                    });
                                    $('.update_book').on("click", function (e) {
                                        
                                    })
                                });
                            }
                        });
                        
                });

            })
            
            // Booking pop-up modal
            $('#booking_and_reservation').off().click(function(evnt){
                
                var appdiv = $('#booking_modal');
                var bk_loader = $('#bk_n_res_loader');
                var product_id = parseInt(appdiv.data('res_id'),10);
                var redirect = window.location.pathname;
                bk_loader.show();
                ajax.jsonRpc("/booking/reservation/modal", 'call',{
                    'product_id' : product_id,
                })
                .then(function (modal) {
                    bk_loader.hide();
                    var $modal = $(modal);
                    $modal.appendTo(appdiv)
                        .modal('show')
                        .on('hidden.bs.modal', function () {
                            $(this).remove();
                        });
                        // Booking Date Selection Picker
                        var today = new Date();
                        var date_default = today.getFullYear()+'-'+("0" + (today.getMonth() + 1)).slice(-2)+'-'+("0" + today.getDate()).slice(-2);
                        var date = new Date();
                        var max_booking = parseInt($('.max_booking').text());
                        date.setDate(date.getDate() + max_booking);
                        var end_date = $('#bk_datepicker').data('bk_end_date')
                        var end_date_date = new Date(end_date)
                        if (date <= end_date_date){
                            end_date = date;
                        }
                        var disabledDate = ( $('#bk_datepicker').data('blocked_date') != undefined) ? $('#bk_datepicker').data('blocked_date') : false
                        $(function () {
                            if ($('#bk_datepicker').length > 0){
                                $('#bk_datepicker').datetimepicker({
                                    format: 'YYYY-MM-DD',
                                    icons: {
                                        date: 'fa fa-calendar',
                                        next: 'fa fa-chevron-right',
                                        previous: 'fa fa-chevron-left',
                                    },
                                    // defaultDate : new Date(),
                                    minDate : $('#bk_datepicker').data('bk_default_date'),
                                    maxDate : end_date,
                                    daysOfWeekDisabled : get_w_closed_days($('#bk_datepicker').data('w_c_days')),
                                    disabledDates: [moment(disabledDate,'YYYY-MM-DD')],
                                });
                            }
                        });
                        console.log(" check modal : ", $modal)
                        $modal.on('click','.bk_slot_div',function(evnt){
                            var $this = $(this);
                            console.log("change slot")
                            var slot_plans = $this.data('slot_plans');
                            var booking_modal = $('.modal_shown').closest('#booking_modal');
                            var bk_loader = $('#bk_n_res_loader');
                            var time_slot_id = parseInt($this.data('time_slot_id'),10);
                            var line_id = booking_modal.data('line_id')
                            if(line_id){
                                line_id = parseInt(line_id,10);
                                var slot_id = parseInt($this.data('slot_id'),10);
                            }
                            
                            var model_plans = booking_modal.find('.bk_model_plans');
                            var seat = booking_modal.find('#array_bk_data').val();
                            if (seat){
                                var seat = JSON.parse(seat);
                            }else{
                                var seat = [];
                            }
                            var bk_modal_slots = booking_modal.find('.bk_modal_slots');
                            var product_id = parseInt(booking_modal.data('res_id'),10);
                            var bk_sel_date = $('#bk_sel_date');
                            bk_loader.show();
                            self.render_seat(booking_modal, [], true);
                            ajax.jsonRpc("/booking/reservation/slot/plans", 'call',{
                                'time_slot_id' : time_slot_id,
                                'slot_plans' : slot_plans,
                                'line_id': line_id,
                                'sel_date' : bk_sel_date.val(),
                                'product_id' : product_id,
                                'seat': seat,
                                'user_id': session.user_id
                            })
                            .then(function (result) {
                                bk_loader.hide();
                                reset_total_price();
                                model_plans.html(result);
                                booking_modal.find('#array_bk_data').val('')
                                if (line_id){
                                    ajax.jsonRpc("/booking/reservation/cart/update_date", 'call',{
                                        'product_id': product_id,
                                        'line_id' : line_id,
                                        'booking_date': bk_sel_date.val(),
                                        'slot_id': slot_id
                                    })
                                }
                            });
                            bk_modal_slots.find('.bk_slot_div').not($this).each(function(){
                                var $this = $(this);
                                if($this.hasClass('bk_active')){
                                    console.log("bk class removed")
                                    $this.removeClass('bk_active');
                                }
                            });
                            if(!$this.hasClass('bk_active')){
                                $this.addClass('bk_active');
                            }
                        });
                        $('#bk_datepicker').on("change.datetimepicker", function (e) {
                        // $('#bk_datepicker').on("dp.change", function (e) {
                            var date = new Date(e.date);
                            var o_date = new Date(e.oldDate);
                            function GetFormate(num){
                                if(num<10)
                                {
                                    return '0'+num;
                                }
                                return num
                            }
                            function GetFormattedDate(date) {
                                var month = GetFormate(date .getMonth() + 1);
                                var day = GetFormate(date .getDate());
                                var year = date .getFullYear();
                                return day + "/" + month + "/" + year;
                            }
                            if(GetFormattedDate(date) != GetFormattedDate(o_date)){
                                bk_loader.show();
                                self.render_seat(appdiv,[],true);
                                ajax.jsonRpc("/booking/reservation/modal/update", 'call',{
                                    'product_id' : product_id,
                                    'new_date' : GetFormattedDate(date),
                                    'user_id': session.user_id
                                })
                                .then(function (result) {
                                    bk_loader.hide();
                                    if((date.getMonth() != o_date.getMonth()) || (date.getFullYear() != o_date.getFullYear())){
                                        var date_str = date.toUTCString();
                                        date_str = date_str.split(' ').slice(2,4)
                                        document.getElementById("dsply_bk_date").innerHTML = date_str.join(", ");
                                    }
                                    var bk_slots_main_div = appdiv.find('.bk_slots_main_div');
                                    reset_total_price();
                                    
                                    bk_slots_main_div.html(result);
                                    $('.modal_shown').closest('#booking_modal').on('click','.bk_slot_div',function(evnt){
                                        var $this = $(this);
                                        console.log("change slot")
                                        var slot_plans = $this.data('slot_plans');
                                        var booking_modal = $('.modal_shown').closest('#booking_modal');
                                        var bk_loader = $('#bk_n_res_loader');
                                        var time_slot_id = parseInt($this.data('time_slot_id'),10);
                                        var line_id = booking_modal.data('line_id')
                                        if(line_id){
                                            line_id = parseInt(line_id,10);
                                            var slot_id = parseInt($this.data('slot_id'),10);
                                        }
                                        
                                        var model_plans = booking_modal.find('.bk_model_plans');
                                        var seat = booking_modal.find('#array_bk_data').val();
                                        if (seat){
                                            var seat = JSON.parse(seat);
                                        }else{
                                            var seat = [];
                                        }
                                        var bk_modal_slots = booking_modal.find('.bk_modal_slots');
                                        var product_id = parseInt(booking_modal.data('res_id'),10);
                                        var bk_sel_date = $('#bk_sel_date');
                                        bk_loader.show();
                                        self.render_seat(booking_modal, [], true);
                                        ajax.jsonRpc("/booking/reservation/slot/plans", 'call',{
                                            'time_slot_id' : time_slot_id,
                                            'slot_plans' : slot_plans,
                                            'line_id': line_id,
                                            'sel_date' : bk_sel_date.val(),
                                            'product_id' : product_id,
                                            'seat': seat,
                                            'user_id': session.user_id
                                        })
                                        .then(function (result) {
                                            bk_loader.hide();
                                            reset_total_price();
                                            model_plans.html(result);
                                            booking_modal.find('#array_bk_data').val('')
                                            if (line_id){
                                                ajax.jsonRpc("/booking/reservation/cart/update_date", 'call',{
                                                    'product_id': product_id,
                                                    'line_id' : line_id,
                                                    'booking_date': bk_sel_date.val(),
                                                    'slot_id': slot_id
                                                })
                                            }
                                        });
                                        bk_modal_slots.find('.bk_slot_div').not($this).each(function(){
                                            var $this = $(this);
                                            if($this.hasClass('bk_active')){
                                                console.log("bk class removed")
                                                $this.removeClass('bk_active');
                                            }
                                        });
                                        if(!$this.hasClass('bk_active')){
                                            $this.addClass('bk_active');
                                            $('.seat-cont').show()
                                        }
                                        
                                    });
                                    var slot_id = $('.bk_slot_div.bk_active')
                                    if (slot_id.length == 0){
                                        $('.seat-cont').hide()
                                    }
                                    else{
                                        $('.seat-cont').show()
                                    }
                                });
                            }
                        });
                });
            });

            // Booking day slot selection
            $('.modal_shown').closest('#booking_modal').on('click','.bk_slot_div',function(evnt){
                var $this = $(this);
                console.log("change slot")
                var slot_plans = $this.data('slot_plans');
                var booking_modal = $('.modal_shown').closest('#booking_modal');
                var bk_loader = $('#bk_n_res_loader');
                var time_slot_id = parseInt($this.data('time_slot_id'),10);
                var line_id = booking_modal.data('line_id')
                if(line_id){
                    line_id = parseInt(line_id,10);
                    var slot_id = parseInt($this.data('slot_id'),10);
                }
                
                var model_plans = booking_modal.find('.bk_model_plans');
                var seat = booking_modal.find('#array_bk_data').val();
                if (seat){
                    var seat = JSON.parse(seat);
                }else{
                    var seat = [];
                }
                var bk_modal_slots = booking_modal.find('.bk_modal_slots');
                var product_id = parseInt(booking_modal.data('res_id'),10);
                var bk_sel_date = $('#bk_sel_date');
                bk_loader.show();
                self.render_seat(booking_modal, [], true);
                ajax.jsonRpc("/booking/reservation/slot/plans", 'call',{
                    'time_slot_id' : time_slot_id,
                    'slot_plans' : slot_plans,
                    'line_id': line_id,
                    'sel_date' : bk_sel_date.val(),
                    'product_id' : product_id,
                    'seat': seat,
                    'user_id': session.user_id
                })
                .then(function (result) {
                    bk_loader.hide();
                    reset_total_price();
                    model_plans.html(result);
                    booking_modal.find('#array_bk_data').val('')
                    if (line_id){
                        ajax.jsonRpc("/booking/reservation/cart/update_date", 'call',{
                            'product_id': product_id,
                            'line_id' : line_id,
                            'booking_date': bk_sel_date.val(),
                            'slot_id': slot_id
                        })
                    }
                });
                bk_modal_slots.find('.bk_slot_div').not($this).each(function(){
                    var $this = $(this);
                    if($this.hasClass('bk_active')){
                        console.log("bk class removed")
                        $this.removeClass('bk_active');
                    }
                });
                if(!$this.hasClass('bk_active')){
                    $this.addClass('bk_active');
                }
            });

            // Booking Week Day Selection
            $('#booking_modal').off().on('click','.bk_days',function(evnt){
                var $this = $(this);
                if($this.hasClass('bk_disable')){
                    return false;
                };
                var booking_modal = $('.modal_shown').closest('#booking_modal');
                var bk_loader = $('#bk_n_res_loader');
                var product_id = parseInt(booking_modal.data('res_id'),10);
                var bk_week_days = booking_modal.find('.bk_week_days');
                var bk_model_cart = booking_modal.find('.bk_model_cart');
                var bk_model_plans = booking_modal.find('.bk_model_plans');
                var bk_slots_n_plans_div = booking_modal.find('.bk_slots_n_plans_div');
                var w_day = $this.data('w_day');
                var w_date = $this.data('w_date');
                var bk_sel_date = $('#bk_sel_date');
                bk_week_days.find('.bk_days').not($this).each(function(){
                    var $this = $(this);
                    if($this.hasClass('bk_active')){
                        console.log("removed here")
                        $this.removeClass('bk_active');
                    }
                });
                if(!$this.hasClass('bk_active')){
                    $this.addClass('bk_active');
                }
                bk_loader.show();
                ajax.jsonRpc("/booking/reservation/update/slots", 'call',{
                    'w_day' : w_day,
                    'w_date' : w_date,
                    'product_id' : product_id,
                })
                .then(function (result) {
                    bk_loader.hide();
                    reset_total_price();
                    bk_slots_n_plans_div.html(result);
                });
                bk_sel_date.val(w_date);
            });

            // Booking quantity Selection
            $('#booking_modal').on('change','.bk_qty_sel',function(evnt){
                var bk_qty = parseInt($(this).val(), 10);
                var booking_modal = $('.modal_shown').closest('#booking_modal');
                // var add_qty = booking_modal.closest('form').find("input[name='add_qty']");
                var bk_base_price = parseFloat(booking_modal.find(".bk_plan_base_price .oe_currency_value").html(), 10);
                var bk_total_price = booking_modal.find('.bk_total_price .oe_currency_value');
                // add_qty.val(bk_qty);
                bk_total_price.html((bk_base_price*bk_qty).toFixed(2));
            });

            // Click on Book Now button on booking modal: submit a form available on product page
            $('#booking_modal').on('click','.bk-submit',function(event){
                var $this = $(this);
                var booking_modal = $('.modal_shown').closest('#booking_modal');
                var bk_loader = $('#bk_n_res_loader');
                var product_id = parseInt(booking_modal.data('res_id'),10);
                var bk_model_plans = booking_modal.find('.bk_model_plans').find("input[name='bk_plan']:checked");
                var bk_modal_err = booking_modal.find('.bk_modal_err');
                if($('.bk_slot_div.bk_active').attr('data-slot_plans') === undefined){
                    return alert('Warning! Booking slots are not available for this date : '+ $('#bk_sel_date').val())
                }
                var slot_id = JSON.parse($('.bk_slot_div.bk_active').attr('data-slot_plans').replace(/'/g, '"').replace(/F/g, 'f'))[0]['id']
                if (booking_modal.find('#array_bk_data').val()){
                    var bk_data = JSON.parse(booking_modal.find('#array_bk_data').val());
                    if (bk_data.length == 0){
                        return alert("Please select seat!")
                    }
                }else{
                    var bk_data = [];
                    return alert("Please select seat!")
                }
                
                if (!event.isDefaultPrevented() && !$this.is(".disabled")) {
                    bk_loader.show();
                    ajax.jsonRpc("/booking/reservation/cart/validate", 'call',{
                        'product_id' : product_id,
                        'booking_ids' : bk_data
                    })
                    .then(function (result) {
                        if(result == true){
                            event.preventDefault();
                            var counter = booking_modal.find('.counter').text();
                            booking_modal.find('#seat_qty').val(counter);
                            booking_modal.find('#slot_id').val(slot_id);
                            $this.closest('form').submit();
                        }
                        else{
                            bk_loader.hide();
                            alert("This movie already in your cart. Please edit from there to add or change the seat.");
                        }
                    });
                }
                // }
            });

            // Booking Slot Plan Selection
            $('.modal_shown').closest('#booking_modal').on('click', "input[name='bk_plan']", function(event){
                var booking_modal = $('.modal_shown').closest('#booking_modal');
                var bk_plan_div = $(this).closest('label').find('.bk_plan_div');
                var bk_plan_base_price = booking_modal.find(".bk_plan_base_price .oe_currency_value");
                var base_price = parseInt(bk_plan_div.data('plan_price'), 10);
                var bk_total_price = booking_modal.find('.bk_total_price .oe_currency_value');
                var bk_qty = parseInt(booking_modal.find('.bk_qty_sel').val(),10);
                if(bk_plan_div.hasClass('bk_disable')){
                    return false;
                };
                if(isNaN(base_price)){
                    base_price = 0.0;
                }
                bk_plan_base_price.html(base_price.toFixed(2));
                bk_total_price.html((base_price*bk_qty).toFixed(2));
            });

            // Click on remove button available on sold out product in cart line
            $('.oe_website_sale').each(function() {
                var oe_website_sale = this;
                
                $(oe_website_sale).on('click', '.remove-cart-line', function() {
                    var $dom = $(this).closest('tr');
                    var td_qty = $dom.find('.remove-cart-line');
                    var line_id = parseInt(td_qty.data('line-id'), 10);
                    var product_id = parseInt(td_qty.data('product-id'), 10);
                    console.log("check product id -----", product_id)
                    ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'line_id': line_id,
                        'product_id': product_id,
                        'set_qty': 0.0
                    })
                    .then(function(data) {
                        var $q = $(".my_cart_quantity");
                        $q.parent().parent().removeClass("hidden", !data.quantity);
                        $q.html(data.cart_quantity).hide().fadeIn(600);
                        location.reload();
                    });
                });
            });
        },
        check_qty_limit: function($modal, sc){
            var conf_qty = $modal.data('max_qty');
            var qty = $modal.parents('.td-product_name').siblings('td.td-qty').find('.js_quantity').val();
            
            var max_qty = conf_qty*qty;
            if(!max_qty){
                return false;
            }
            var selected_qty = sc.find('selected').length + 1
            console.log("check qty: ",max_qty, selected_qty);
            if (selected_qty > max_qty){
                return true;
            }

            return false;
            


            
        },
        render_seat: function($modal, seats_unavailable, clear_selected, seat_selected) {
            var self = this;
            var $modalshown =  $('.modal_shown').closest('#booking_modal');
            
            function recalculateTotal(sc, data) {
                var total = 0;
                console.log("SC ------------",data.data())
                //basically find every selected seat and sum its price
                // sc.find('selected').each(function () {
                //     total += this.data().price;
                //     console.log("total selected :",total)
                // });

                for (var s=0;s<sc.find('selected').seatIds.length;s++){
                    total += data.data().price;
                    console.log("total selected :",total)
                };
                
                return total;
            }
            function removewithfilter(arr) { 
                let outputArray = arr.filter(function(v, i, self) 
                { 
                    return i == self.indexOf(v); 
                }); 
                  
                return outputArray; 
            } 
            var sc = $modal.find('#seats-ecom').seatCharts({
                map: [
                    'b[l1,1]f[l2,2]b[l3,3]f[l4,4]b[l5,5]f[l6,6]b[l7,7]___b[l8,8]f[l9,9]b[l10,10]f[l11,11]b[l12,12]f[l13,13]b[l14,14]f[l15,15]b[l16,16]f[l17,17]b[l18,18]f[l19,19]___b[l20,20]f[l21,21]b[l22,22]f[l23,23]b[l24,24]f[l25,25]b[l26,26]',
                    'f[k1,1]b[k2,2]f[k3,3]b[k4,4]f[k5,5]b[k6,6]f[k7,7]___f[k8,8]b[k9,9]f[k10,10]b[k11,11]f[k12,12]b[k13,13]f[k14,14]b[k15,15]f[k16,16]b[k17,17]f[k18,18]b[k19,19]___f[k20,20]b[k21,21]f[k22,22]b[k23,23]f[k24,24]b[k25,25]f[k26,26]',
                    'b[j1,1]f[j2,2]b[j3,3]f[j4,4]b[j5,5]f[j6,6]b[j7,7]f[j8,8]_f[j9,9]b[j10,10]f[j11,11]b[j12,12]f[j13,13]b[j14,14]f[j15,15]b[j16,16]f[j17,17]b[j18,18]f[j19,19]b[j20,20]f[j21,21]b[j22,22]_f[j23,23]b[j24,24]f[j25,25]b[j26,26]f[j27,27]b[j28,28]f[j29,29]b[j30,30]',
                    'f[i1,1]b[i2,2]f[i3,3]b[i4,4]f[i5,5]b[i6,6]f[i7,7]b[i8,8]_b[i9,9]f[i10,10]b[i11,11]f[i12,12]b[i13,13]f[i14,14]b[i15,15]f[i16,16]b[i17,17]f[i18,18]b[i19,19]f[i20,20]b[i21,21]f[i22,22]_b[i23,23]f[i24,24]b[i25,25]f[i26,26]b[i27,27]f[i28,28]b[i29,29]f[i30,30]',
                    'b[h1,1]f[h2,2]b[h3,3]f[h4,4]b[h5,5]f[h6,6]b[h7,7]f[h8,8]_f[h9,9]b[h10,10]f[h11,11]b[h12,12]f[h13,13]b[h14,14]f[h15,15]b[h16,16]f[h17,17]b[h18,18]f[h19,19]b[h20,20]f[h21,21]b[h22,22]_f[h23,23]b[h24,24]f[h25,25]b[h26,26]f[h27,27]b[h28,28]f[h29,29]b[h30,30]',
                    'f[g1,1]b[g2,2]f[g3,3]b[g4,4]f[g5,5]b[g6,6]f[g7,7]b[g8,8]_b[g9,9]f[g10,10]b[g11,11]f[g12,12]b[g13,13]f[g14,14]b[g15,15]f[g16,16]b[g17,17]f[g18,18]b[g19,19]f[g20,20]b[g21,21]f[g22,22]_b[g23,23]f[g24,24]b[g25,25]f[g26,26]b[g27,27]f[g28,28]b[g29,29]f[g30,30]',
                    'b[f1,1]f[f2,2]b[f3,3]f[f4,4]b[f5,5]f[f6,6]b[f7,7]f[f8,8]_f[f9,9]b[f10,10]f[f11,11]b[f12,12]f[f13,13]b[f14,14]f[f15,15]b[f16,16]f[f17,17]b[f18,18]f[f19,19]b[f20,20]f[f21,21]b[f22,22]_f[f23,23]b[f24,24]f[f25,25]b[f26,26]f[f27,27]b[f28,28]f[f29,29]b[f30,30]',
                    'f[e1,1]b[e2,2]f[e3,3]b[e4,4]f[e5,5]b[e6,6]f[e7,7]b[e8,8]_b[e9,9]b[e10,10]b[e11,11]b[e12,12]b[e13,13]f[e14,14]b[e15,15]f[e16,16]b[e17,17]f[e18,18]b[e19,19]b[e20,20]b[e21,21]b[e22,22]_b[e23,23]f[e24,24]b[e25,25]f[e26,26]b[e27,27]f[e28,28]b[e29,29]f[e30,30]',
                    'b[d1,1]f[d2,2]b[d3,3]f[d4,4]b[d5,5]f[d6,6]b[d7,7]f[d8,8]_b[d9,9]b[d10,10]b[d11,11]b[d12,12]b[d13,13]b[d14,14]b[d15,15]b[d16,16]b[d17,17]b[d18,18]b[d19,19]b[d20,20]b[d21,21]b[d22,22]_f[d23,23]b[d24,24]f[d25,25]b[d26,26]f[d27,27]b[d28,28]f[d29,29]b[d30,30]',
                    'f[c1,1]b[c2,2]f[c3,3]b[c4,4]f[c5,5]b[c6,6]f[c7,7]b[c8,8]_b[c9,9]b[c10,10]b[c11,11]b[c12,12]b[c13,13]b[c14,14]b[c15,15]b[c16,16]b[c17,17]b[c18,18]b[c19,19]b[c20,20]b[c21,21]b[c22,22]_b[c23,23]f[c24,24]b[c25,25]f[c26,26]b[c27,27]f[c28,28]b[c29,29]f[c30,30]',
                    'b[b1,1]f[b2,2]b[b3,3]f[b4,4]b[b5,5]f[b6,6]b[b7,7]f[b8,8]_b[b9,9]b[b10,10]b[b11,11]b[b12,12]b[b13,13]b[b14,14]b[b15,15]b[b16,16]b[b17,17]b[b18,18]b[b19,19]b[b20,20]b[b21,21]b[b22,22]_f[b23,23]b[b24,24]f[b25,25]b[b26,26]f[b27,27]b[b28,28]f[b29,29]b[b30,30]',
                    'h[a1,1]h[a2,2]h[a3,3]h[a4,4]h[a5,5]h[a6,6]h[a7,7]h[a8,8]_b[a9,9]b[a10,10]b[a11,11]b[a12,12]b[a13,13]b[a14,14]b[a15,15]b[a16,16]b[a17,17]b[a18,18]b[a19,19]b[a20,20]b[a21,21]b[a22,22]_b[a23,23]f[a24,24]b[a25,25]f[a26,26]b[a27,27]f[a28,28]b[a29,29]f[a30,30]',
                ],
                seats: {
                    f: {
                        price   : parseFloat($('.oe_price_h4 .oe_price').text()),
                        classes : 'first-class', //your custom CSS class
                        category: 'First Class'
                    },  
                    b: {
                        price   : 0,
                        classes : 'unblocked', //your custom CSS class
                        category: 'Unblocked',
                        click: function(){
                            console.log("clicked")
                            // if (line.seat_number.includes(this.settings.id)){
                            //     line.seat_number.splice( line.seat_number.indexOf(this.settings.id), 1 );
                            // }
                        }
                    },
                    h: {
                        price   : parseFloat($('.oe_price_h4 .oe_price').text()),
                        classes : 'handicapped', //your custom CSS class
                        category: 'handicapped',
                    },      
                },
                naming : {
                    top : false,
                    left: true,
                    getLabel : function (character, row, column) {
                        return column;
                    },
                },
                legend : {
                    node : $('#legend'),
                    items : [
                    [ 'f', 'available',   'Available' ],
                    [ 'f', 'unavailable', 'Occupied'],
                    [ 'f', 'selected', 'Selected'],
                    [ 'b', 'unblocked', 'Blocked'],
                    [ 'h', 'handicapped', 'Wheelchair Berth Available'],
                    [ 'h', 'handicapped unavailable', 'Wheelchair Berth Occupied'],
                    [ '_', 'seatCharts-space', 'Safe Distance'],
                    ]            
                },
                click: function () {
                    $.blockUI({
                        css: {
                            backgroundColor: 'transparent',
                            border: 'none'
                        },
                            baseZ: 1500,
                            overlayCSS: {
                            backgroundColor: '#FFFFFF',
                            opacity: 0.7,
                            cursor: 'wait'
                        }
                    })
                    var line_id = $modal.data('line_id');
                    if (line_id){
                        line_id = parseInt(line_id,10);
                        
                        self.line_id = line_id;
                    }
                    var $modalshown = $('.modal_shown').closest('#booking_modal')
                    

                    var $counter = $modalshown.find('.counter');
                    var $total = $modalshown.find('.bk_total_price .oe_currency_value'); 
                    var max_reached = self.check_qty_limit($modalshown, sc);
                    if (max_reached && this.status() == 'available' && this.settings.data.classes != 'unblocked'){
                        alert("Maximum quantity reached");
                        $.unblockUI();
                        return 'available';
                    }   
                    self.toggle_book_seat(this, $modalshown)
                    if (this.status() == 'available' && this.settings.data.classes != 'unblocked') {
                        $counter.text(sc.find('selected').length+1);
                        $total.text(parseFloat((recalculateTotal(sc, this)+this.data().price).toFixed(2)));
                        // $.unblockUI();
                        return 'selected';
                    } else if (this.status() == 'selected') {
                        //update the counter
                        $counter.text(sc.find('selected').length-1);
                        //and total
                        $total.text(parseFloat((recalculateTotal(sc, this)-this.data().price).toFixed(2)));
                        //remove the item from our cart
                        $('#cart-item-'+this.settings.id).remove();
                        //seat has been vacated
                        // $.unblockUI();
                        return 'available';
                    } else if (this.status() == 'unavailable') {
                        //seat has been already booked
                        // $.unblockUI();
                        return 'unavailable';
                    } else {
                        // $.unblockUI();
                        return this.style();
                    }
                }
                
            });
            if(sc != undefined){
                var oldbook = sc.find('unavailable').seatIds;
                var messyseat = seats_unavailable.concat(oldbook);
                var seat_available = removewithfilter(messyseat)            
                sc.get(seats_unavailable).status('unavailable');
                if (oldbook.length > 0 && JSON.stringify(seat_available)!=JSON.stringify(seats_unavailable) ){
                    sc.get(seat_available).status('available');
                }
                
                if (clear_selected){
                    
                    var sel = sc.find('selected').seatIds;
                    sc.get(sel).status('available');
                    self.seat_number = [];
                    
                }
                console.log("selected_seat: ",self.seat_number, seat_selected);
                sc.get(self.seat_number).status('selected');
                sc.get(seat_selected).status('selected');                
                self.sc = sc;
            }
        },
        poll: function () {
            var self = this;
            var booking_modal = $('.modal_shown').closest('#booking_modal');
            var product_id = parseInt(booking_modal.data('res_id'),10);
            var line_id = parseInt(booking_modal.data('line_id'),10);
            console.log("product_id ----",product_id)
            var book_slot = booking_modal.find('.bk_slot_div.bk_active').attr('data-slot_plans')
            if (book_slot) {
                self.booking_slot_id = JSON.parse(booking_modal.find('.bk_slot_div.bk_active').attr('data-slot_plans').replace(/'/g, '"').replace(/F/g, 'f'))[0]['id']
            }
            self.booking_date = booking_modal.find('#bk_sel_date').val();
            var ts = booking_modal.find('.bk_slot_div.bk_active')
            console.log("check self booking data :",self)
            if (ts.length > 0){
                self.time_slot_id = parseInt(booking_modal.find('.bk_slot_div.bk_active').attr('data-time_slot_id'));
            }
            
            self.$seatcont = $('.seat-cont');
            console.log("session -- : ",session, self)
            if (self.$seatcont && self.booking_date && self.booking_slot_id){
                var booking = {
                    "booking_date": self.booking_date,
                    "booking_slot_id": self.booking_slot_id,
                    "time_slot_id": self.time_slot_id,
                    "product_id": product_id,
                    "source": "ecommerce",
                    "user_id": session.user_id,
                    "sale_line_id": line_id
                }
                ajax.jsonRpc('/seat/poll', 'call', {'booking': booking}).then(function(data) {
                    if(data.success === true) {
                        self.render_seat(self.$seatcont, data.seats, true, data.seats_notpaid);
                    }
                })
            }
            self.startPolling();
        },
        processPolledData: function (seats) {
            console.log("change color",seats)
            for(var i=0;i<seats.length;i++){
                var s = seats[i];
                if (s.book && session.user_id == s.user_id){
                    $('.seat#'+s.id).css('background-color','green')
                }
                else if(s.book && session.user_id != s.user_id){
                    $('.seat#'+s.id).css('background-color','red')
                }
                else {
                    $('.seat#'+s.id).css('background-color','white')
                }
            }
        },
    }); 
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');
    var VariantMixin = require('sale.VariantMixin');
    console.log("VariantMixin", VariantMixin)
    
    
    

    publicWidget.registry.WebsiteSale.include({
        _applyHash: function () {
            var hash = window.location.hash.substring(1);
            if (hash) {
                var params = $.deparam(hash);
                if (params['attr']) {
                    var attributeIds = params['attr'].split(',');
                    var $inputs = this.$('input.js_variant_change, select.js_variant_change option');
                    _.each(attributeIds, function (id) {
                        console.log("variant change")
                        var $toSelect = $inputs.filter('[data-value_id="' + id + '"]');
                        if ($toSelect.is('input[type="radio"]')) {
                            $toSelect.prop('checked', true).trigger("click");
                        } else if ($toSelect.is('option')) {
                            $toSelect.prop('selected', true).trigger("click");
                        }
                    });
                    this._changeColorAttribute();
                }
            }
        },
        onClickAddCartJSON: function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.input-group').find("input");
            if ($link.has(".fa-minus").length > 0){
                var lineid = $input.data('lineId');
                this._rpc({
                    route: "/reservation/clearbook",
                    params: {
                        line_id: lineid,
                    },
                })
                
            }
            
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
    
            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
            return false;
        },
        _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
            _.each($dom_optional, function (elem) {
                $(elem).find('.js_quantity').text(value);
                productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);
            $.blockUI()
            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: parseInt($input.data('product-id'), 10),
                    set_qty: value
                },
            }).then(function (data) {
                $input.data('update_change', false);
                var check_value = parseInt($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger('change');
                    return;
                }
                if (!data.cart_quantity) {
                    return window.location = '/shop/cart';
                }
                wSaleUtils.updateCartNavBar(data);
                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
    
                if (data.warning) {
                    var cart_alert = $('.oe_cart').parent().find('#data_warning');
                    if (cart_alert.length === 0) {
                        $('.oe_cart').prepend('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">'+
                                '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning + '</div>');
                    }
                    else {
                        cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning);
                    }
                    $input.val(data.quantity);
                }
                var seatbook = new publicWidget.registry.SeatBook();
                seatbook.event_listener();
                if (publicWidget.registry.Loyalty){
                    var loyalty = new publicWidget.registry.Loyalty();
                    loyalty.event_listener();
                }
                $.unblockUI()
            });
        },
    })
});
