odoo.define('wesite_booking_system.pos_booking_screen', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;
    var field_utils = require('web.field_utils');
    var qweb = core.qweb;
    var popups = require('point_of_sale.popups');
    var screens = require('point_of_sale.screens');
    var framework = require('web.framework');

    var Days = {
        'sun' : 0,
        'mon' : 1,
        'tue' : 2,
        'wed' : 3,
        'thu' : 4,
        'fri' : 5,
        'sat' : 6,
    }

    _.each(gui.Gui.prototype.popup_classes, function (o) {
        if (o.name == "confirm") {
            var confirmPopupWidget = o.widget;
            confirmPopupWidget.include({
                show: function(options){
                    this._super(options);
                    this.$('.footer .cancel').text(options.label_no)
                    if (options.hide_yes){
                        this.$('.footer .confirm').hide()
                    }


                }
            })
        }
    });

    screens.ActionpadWidget.include({
        /*
                validation payment
                auto ask need apply promotion
                auto ask when have customer special discount
         */
        renderElement: function () {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var lines = order.get_orderlines();
                var confirm = false;
                for (var i=0;i<lines.length;i++){
                    var line = lines[i];
                    var booking_type = line.get_product().is_booking_type || line.check_combo_is_booking_type();
                    
                    if (booking_type){
                        confirm = true;
                    }
                    if (booking_type && !line.check_seatbook()){
                        confirm = false;
                        var bookstr = 'select the booking';
                        if (line.is_return || line.is_exchange){
                            bookstr = 'cancel the booking';
                        }
                        self.pos.gui.show_popup('confirm', {
                            title: 'Warning',
                            body: 'You havent '+bookstr+' detail for '+line.get_product().name+' !',
                            cancel: function () {
                                self.pos.gui.show_screen('products');
                            },
                            hide_yes: true
                        })
                    }
                }

                if (confirm){
                    
                    self.pos.gui.show_popup('confirm', {
                        title: 'Are you sure ?',
                        body_html: self.pos.get_order().get_seat_booking_detail(),
                        cancel: function () {
                            self.pos.gui.show_screen('products');
                        },
                        confirm: function () {
                            if (order.is_exchange){
                                self.pos.gui.show_screen('products');
                                self.pos.gui.show_popup('popup_confirm_payment_switch_sign_sdc')
                            } 
                            if (order.is_return){
                                self.pos.gui.show_screen('products');
                                self.pos.gui.show_popup('popup_confirm_return', {
                                    title: 'Input Manager Password to Continue',
                                })
                            } 
                        },
                        label_no: 'No'
                    })
                }
                
            })
        }
    })
    var seat_popup = popups.extend({
        template: 'SlotBooking',
        get_unavailable_seat: function(booking){
            
            return rpc.query({
                model: 'seat.book',
                method: 'get_unavailable',
                args: [booking],
            })
        },
        unbook_seatnumber: function(seats_numbers){
            var old_seat = seats_numbers;
            if (!seats_numbers){
                return;
            }
            var self = this;
            var order = self.pos.get_order();
            var line = order.selected_orderline;
            var seat_data  = {
                'booking_date' : line.booking_date,
                'booking_slot_id': line.booking_slot_id,
                'seat_ids': seats_numbers,
                'book': false,
                'user_id': self.pos.get_cashier().user_id[0]
            }
            rpc.query({
                model: 'seat.book',
                method: 'unbook_seats',
                args: [seat_data],
            }).then(function(){
                order.selected_orderline.seat_number = [];
                order.selected_orderline.trigger('change', order.selected_orderline);
                if(self.sc){
                    self.sc.get(old_seat).status('available');
                } 
            })
            
        },
        toggle_book_seat: function(seat){
            framework.blockUI();
            var self = this;
            var order = self.pos.get_order();
            var line = order.selected_orderline;
            var seat_data = {}
            var $counter = $('#counter');
            var $counterreturn = $('#counter-return');
            var product_tmpl_id , product_id , product

            if ((line.is_return || line.is_exchange) && self.reach_maxreturn(parseInt($counterreturn.text()))){
                framework.unblockUI();
                return self.pos.gui.show_popup('confirm', {
                    title: 'Warning',
                    body: 'Maximum Unbook QTY reached',
                    cancel: function () {
                        self.gui.show_popup("seat-book", {'product-id': line.product.id});
                    },
                    hide_yes:true,
                    change_label_no:'OK',
                })
            }
            if(line.check_combo_is_booking_type() && parseInt($counter.text()) >= line.get_product_combo_items(self.product_id).quantity * line.quantity && seat.status()== 'available'){
                framework.unblockUI();
                return self.pos.gui.show_popup('confirm', {
                    title: 'Warning',
                    body: 'Maximum Seat QTY reached',
                    cancel: function () {
                        self.gui.show_popup("seat-book", {'product-id': self.product_id, 'seat_type':'bundle', 'combo_item_index': self.combo_item_index});
                    },
                    hide_yes:true,
                    change_label_no:'OK',
                })
            }
            if(line.redeem_ticket && seat.status()== 'available'){
                console.log("check qty :",line.seat_number.length-1,line.quantity)
                if (line.seat_number.length > line.quantity-1){
                    framework.unblockUI();
                    return self.pos.gui.show_popup('confirm',{
                        title: 'Information',
                        body: 'Sorry, you have reached your limit to redeem the ticket!',
                        hide_yes: true,
                        cancel: function () {
                            self.gui.close_popup();
                            self.gui.show_popup("seat-book", {'product-id': line.product.id,'seat_type':'line'});
                        },
                    });   
                }
                // reward_button.check_redeemed_ticket(line.order, line.order.get_client(), line.reward).then(funtion(qty_left){
                    
                // })
                // if(parseInt($counter.text()) > 0){
                   
                // }
                // else if(!){
                //     framework.unblockUI();
                //     return self.pos.gui.show_popup('confirm',{
                //         title: 'Information',
                //         body: 'Sorry, you have reached your limit to redeem the ticket!',
                //         hide_yes: true,
                //         cancel: function () {
                //             self.gui.close_popup();
                //             self.gui.show_popup("seat-book", {'product-id': line.product.id,'seat_type':'line'});
                //         },
                //     });
                // }
            }
            if(line.redeem_ticket_employee && seat.status()== 'available'){
                var redeemed_employee_button = self.pos.gui.current_screen.action_buttons.redeem_ticket_employee_button
                if(!redeemed_employee_button.check_available_quota(order, line.seat_number.length)){
                    framework.unblockUI();
                    seat_data  = {
                        'booking_date' : line.booking_date,
                        'booking_slot_id': line.booking_slot_id,
                        'seat_id': seat.settings.id,
                        'book': true,
                        'user_id': self.pos.get_cashier().user_id[0]
                    }
                    return this.gui.show_popup('popup_confirm_return', {
                        title: 'Information',
                        body: 'Sorry, you have reached your limit to redeem the ticket!  \n Input Manager Password to Continue',
                        cancel_auth_title: 'Refuse',
                        redeem_ticket: true,
                        product_id: line.product.id,
                        back_popup: 'seat-book', 
                        seat_data: seat_data,
                        
                    })
                }
            }
           
            if(self.seat_type == 'line'){
                product = self.booking_data.product
                product_tmpl_id = self.booking_data.product.product_tmpl_id

            }
            else if(self.seat_type == 'bundle'){
                product_id = self.booking_data.product_id[0]
                product = this.pos.db.product_by_id[product_id]
                product_tmpl_id =product.product_tmpl_id
                if (!self.booking_data.seat_number){
                    self.booking_data.seat_number = []
                }
                self.booking_data.seat_number_return = []
            }
            seat_data  = {
                'booking_date' : self.booking_data.booking_date,
                'booking_slot_id': self.booking_data.booking_slot_id,
                'seat_id': seat.settings.id,
                'product_id': product_tmpl_id,
                'user_id': self.pos.get_cashier().user_id[0],
                'barcode': self.pos.get_order().generate_barcode(product),
                'order_reference': self.pos.get_order().selected_orderline.cid
            }
            if (seat.status() == 'available'){
                if (line.is_return || line.is_exchange){
                    framework.unblockUI();
                    return self.pos.gui.show_popup('confirm', {
                        title: 'Warning',
                        body: 'Please only select the booked seat',
                        cancel: function () {
                            self.gui.show_popup("seat-book", {'product-id': line.product.id,'seat_type':'line'});
                        },
                        hide_yes:true,
                        change_label_no:'OK',
                    })
                }
                seat_data.book = true
                self.booking_data.seat_number.push(seat.settings.id)
                self.booking_data.seat_number_return.splice( self.pos.get_order().selected_orderline.seat_number_return.indexOf(seat.settings.id), 1 );
                
            }else if (seat.status() == 'selected'){
                seat_data.book = false
                self.booking_data.seat_number_return.push(seat.settings.id)
                self.booking_data.seat_number.splice( self.pos.get_order().selected_orderline.seat_number.indexOf(seat.settings.id), 1 );
            }
            else if (seat.status() == 'unavailable'){
                framework.unblockUI();
                return false;
            }
            order.selected_orderline.trigger('change', order.selected_orderline);
            order.trigger('change', order);
            
            rpc.query({
                model: 'seat.book',
                method: 'togglebook',
                args: [seat_data],
            }).then(function(results){
                // for (var i = 0; i < results.length; i++) {
                //     var res = results[i];
                //     res.barcode_order = self.pos.get_order().generate_barcode(product)
                // }
                if(!self.booking_data.seat_barcodes){
                    self.booking_data.seat_barcodes = [];
                }
                for (var i=0;i<results.length;i++){
                    var s = results[i];
                    if(s.book){
                        self.booking_data.seat_barcodes.push(s)
                    }else{
                        var temp_seat = self.booking_data.seat_barcodes
                        for(var z=0;z<self.booking_data.seat_barcodes.length;z++){
                            var se = self.booking_data.seat_barcodes[z];
                            if (se['name'] == s['name']){
                                temp_seat.splice(z, 1);
                            }
                        }
                        self.booking_data.seat_barcodes = temp_seat;
                    }
                    
                }
                var last_running_number = self.pos.increment_running_number(product)
                self.booking_data.last_running_number = last_running_number
                line.trigger('change', line);
                order.trigger('change', order);
                framework.unblockUI();
                
            })

            
        },
        change_day_slot: function(e, self){
            var selected_day = false;
            var order = self.pos.get_order();
            
            var d = false;
            if (e && e.date){
                d = e.date._d;
                selected_day = e.date.days();
                
            } else {
                d = new Date(self.booking_data.booking_date);
                selected_day = d.getDay()

            }
            
            
            for (var x=0;x<self.days_slot.length;x++){
                var day_slot = self.days_slot[x]
                if (Days[day_slot.name] == selected_day){
                    self.selected_day = day_slot;
                }
            }
            if (!self.selected_day){
                return false;
            }
            var time_slots = self.pos.time_slot_by_day_id[self.selected_day.id];
            var ts_final = []
            for (var i=0;i<time_slots.length;i++){
                time_slots[i].start_time = time_slots[i].display_name.split('-')[0]
                var ts = time_slots[i];
                var cd = new Date();
                
                var times = ts.display_name.split('-')[1];
                var hour = times.split(':')[0];
                var time = times.split(':')[1];
                d.setMinutes(time);
                d.setHours(hour);

                if (d > cd){
                    ts_final.push(ts)
                }
                

            }
            
            var time_slot_html = qweb.render('TimeSlot', {time_slots: ts_final, widget: self});
            var div = document.createElement('div');
            div.innerHTML = time_slot_html;
            var list_container = document.querySelector('.time-slot');
            list_container.innerHTML = '';
            if (list_container) {
                list_container.appendChild(div);
            }
            // self.$(".time-slot-option").hover(function() {
            //     self.$('.time-slot-option-label').css("background-color","white");
            //     $(this).next().css("background-color","lightblue");
            // });
            self.$('.time-slot-option').click(function(e){
                var id = $(this).attr('data-id');
                self.$('.time-slot-option-label').css("background-color","white");
                $(this).next().css("background-color","lightblue")
                if (self.booking_data.booking_slot_id != parseInt(id)){
                    console.log("change time slot unbook seat")
                    self.unbook_seatnumber(self.booking_data.seat_number);
                }

                self.booking_data.booking_slot_id = parseInt(id);
                order.selected_orderline.trigger('change', order.selected_orderline);
                if (self.booking_data && self.booking_data.booking_slot_id)
                {
                    $('.seat-cont').show();
                }
                order.trigger('change', order);
                
            });
            self.$('.date-temp').text(self.$('.day-slot').val())
            
        },
        render_seat: function(seats_unavailable){
            console.log("render seat")
            var self = this;
            var order = self.pos.get_order();
            var line = order.selected_orderline;
            if (!line){
                return
            }
            function recalculateTotal(sc) {
                var total = 0;
              
                //basically find every selected seat and sum its price
                sc.find('selected').each(function () {
                  total += this.data().price;
                });
                
                return total;
            }
            function removewithfilter(arr) { 
                let outputArray = arr.filter(function(v, i, self) 
                { 
                    return i == self.indexOf(v); 
                }); 
                  
                return outputArray; 
            } 
            var $counter = $('#counter');
            var $total = $('#total');
            var $counterreturn = $('#counter-return');
            if (line.seat_number_return){
                $counterreturn.text(line.seat_number_return.length);
            }
            if(self.booking_data.seat_number){
                $counter.text(self.booking_data.seat_number.length);
                $total.text(line.get_unit_price()*self.booking_data.seat_number.length);
            }
            
            var sc = $('#seat-map').seatCharts({
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
                        price   : self.pos.get_order().selected_orderline.get_unit_price(),
                        classes : 'first-class', //your custom CSS class
                        category: 'First Class'
                    },  
                    b: {
                        price   : 0,
                        classes : 'unblocked', //your custom CSS class
                        category: 'Unblocked',
                        click: function(){
                            if (self.booking_data.seat_number.includes(this.settings.id)){
                                self.booking_data.seat_number.splice( self.booking_data.seat_number.indexOf(this.settings.id), 1 );
                            }
                            
                        }
                    },  
                    h: {
                        price   : self.pos.get_order().selected_orderline.get_unit_price(),
                        classes : 'handicapped', //your custom CSS class
                        category: 'handicapped',
                    },
                
                },
                naming : {
                    top : false,
                    left: true,
                    getLabel : function (character, row, column) {
                        return column;
                    // return firstSeatLabel++;
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
                    self.toggle_book_seat(this);
                    if (this.status() == 'available' && this.settings.data.classes != 'unblocked') {
                        $counter.text(sc.find('selected').length+1);
                        $counterreturn.text(sc.find('selected').length-1);
                        $total.text(recalculateTotal(sc)+this.data().price);
                        return 'selected';
                    // }
                    // else if (this.settings.data.classes == 'unblocked'){
                    //     return 'unavailable';
                    
                    } else if (this.status() == 'selected') {
                        //update the counter
                        $counter.text(sc.find('selected').length-1);
                        $counterreturn.text(sc.find('selected').length+1);
                        //and total
                        $total.text(recalculateTotal(sc)-this.data().price);
                        //remove the item from our cart
                        $('#cart-item-'+this.settings.id).remove();
                        //seat has been vacated
                        return 'available';
                    } else if (this.status() == 'unavailable') {
                        //seat has been already booked
                        return 'unavailable';
                    } else {
                        return this.style();
                    }
                }
            });
            if(!sc){
                return;
            }

            //this will handle "[cancel]" link clicks
            $('#selected-seats').on('click', '.cancel-cart-item', function () {
                sc.get($(this).parents('li:first').data('seatId')).click();
            });
           
            var oldbook = sc.find('unavailable').seatIds;
            var messyseat = seats_unavailable.concat(oldbook);
            var seat_available = removewithfilter(messyseat)            
            sc.get(seats_unavailable).status('unavailable');
            if (oldbook.length > 0 && JSON.stringify(seat_available)!=JSON.stringify(seats_unavailable) ){
                sc.get(seat_available).status('available');
            }
            var sel_seat = self.pos.get_order().selected_orderline.seat_number;
            if(self.seat_type == 'bundle'){
                sel_seat = self.booking_data.seat_number;
            }
            if (typeof sel_seat === 'string'){
                sel_seat = JSON.parse(sel_seat);
            } 
            sc.get(sel_seat).status('selected');
            self.sc = sc;
        },
        
        unbook_seatnumber: function(seats_numbers){
            var old_seat = seats_numbers;
            if (!seats_numbers){
                return;
            }
            var self = this;
            var order = self.pos.get_order();
            var line = order.selected_orderline;
            var seat_data  = [{
                'booking_date' : line.booking_date,
                'booking_slot_id': line.booking_slot_id,
                'seat_ids': seats_numbers,
                'book': false,
                'user_id': self.pos.get_cashier().user_id[0]
            }]
            rpc.query({
                model: 'seat.book',
                method: 'unbook_seats',
                args: [seat_data],
            }).then(function(){
                order.selected_orderline.seat_number = [];
                order.selected_orderline.trigger('change', order.selected_orderline);
                if(self.sc){
                    self.sc.get(old_seat).status('available');
                } 
            })
        },

        show: function (options) {
            var self = this;
            
            self.seat_type = options['seat_type']
            self.combo_item_index = options['combo_item_index']
            if(self.seat_type == 'line'){
                self.booking_data = self.pos.get_order().selected_orderline
            }
            else if(self.seat_type == 'bundle'){
                self.booking_data  = self.pos.get_order().selected_orderline.combo_items[parseInt(self.combo_item_index)];
            }
            self.booking_data.cid = self.pos.get_order().selected_orderline.cid 
            this.poll()
            this._super(options);
            
            self.product_id = options['product-id'];
            self.end_data = ''
            self.default_date = ''
            self.w_closed_days =  ''
            var days = ['mon','tue','wed','thu','fri','sat','sun'];
            self.closed_days = [];
            self.prod = self.pos.db.get_product_by_id(self.product_id);
            self.days_slot = self.pos.day_slot_by_tmpl_id[self.prod.product_tmpl_id];
            self.blocked_date = self.prod.blocked_date

            if (self.pos.get_order().selected_orderline.is_return || self.pos.get_order().selected_orderline.is_exchange){
                self.$('.left-side').hide();
                self.$('.right-side').hide();
                self.$('.card-title').text('UNBOOK YOUR SEAT');
                self.$('.select-date').hide();
            }
            if (!self.days_slot){
                console.log("check day slot: ",self)
                return
                // return self.pos.gui.show_popup('dialog', {
                //     title: 'WARNING',
                //     from: 'top',
                //     align: 'center',
                //     body: 'No booking slot configured',
                //     color: 'danger',
                // });
            }
            for (var i=0;i<self.days_slot.length;i++){
                var d = self.days_slot[i];
                days.splice( days.indexOf(d.name), 1 );
            }

            for (var i=0;i<days.length;i++){
                var d = days[i]
                self.closed_days.push(Days[d])
            }
            var today = new Date();
            var date = today.getFullYear()+'-'+("0" + (today.getMonth() + 1)).slice(-2)+'-'+("0" + today.getDate()).slice(-2);
            if (self.product_id && self.prod )
            {
                self.end_data = self.prod.br_end_date;
                self.default_date = date;
                self.w_closed_days = days;
            }
            var date = new Date();
            if (self.pos.config.advance_booking && self.pos.config.advance_booking > 0){
                date.setDate(date.getDate() + self.pos.config.advance_booking);
                self.$('.advance_booking').text(self.pos.config.advance_booking)
                console.log("date :",date, typeof(date), "end_Date: ",self.end_data, typeof(self.end_data))
                if (self.end_data.includes(' ')){
                    self.end_data = self.end_data.split(' ')[0]

                }
                var parts =self.end_data.split('-');
                // Please pay attention to the month (parts[1]); JavaScript counts months from 0:
                // January - 0, February - 1, etc.
                var end_date = new Date(parts[0], parts[1] - 1, parts[2]); 
                if (date <= end_date){
                    self.end_data = date;
                }
                if (self.default_date > date){
                    self.pos.gui.show_popup("error", {
                        'title': _t("Not Available"),
                        'body':  _t("Booking not available yet. Booking in advance max 7 Days"),
                    });
                }
                
            }
            try {
                var dateNow = new Date();
                var dateMonth = dateNow.getMonth() + 1
                var dateMonthString;
                if(dateMonth < 10){
                    dateMonthString = '0' + dateMonth.toString()
                }else{
                    dateMonthString = dateMonth.toString()
                }
                var dateString = dateNow.getFullYear().toString() + "-" + dateMonthString + "-" + dateNow.getDate().toString()
                self.$('.datetimepicker').datetimepicker({
                    format: 'YYYY-MM-DD',
                    // defaultDate: dateString,
                    useCurrent: true,
                    icons: {
                        date: 'fa fa-calendar',
                        next: 'fa fa-chevron-right',
                        previous: 'fa fa-chevron-left',
                    },
                    minDate : self.default_date,
                    maxDate : self.end_data,
                    daysOfWeekDisabled : self.closed_days,
                    disabledDates : [moment(self.blocked_date,'YYYY-MM-DD')],
                });
            }
            catch(err) {
                console.log(err)
                this.pos.gui.show_popup("error", {
                    'title': _t("Not Available"),
                    'body':  _t("Seats are fully booked"),
                });
            }
            if(!self.booking_data.booking_date){
                self.booking_data.booking_date = dateString
            }
            if (!self.booking_data.booking_date){
                this.$('.day-slot').trigger('dp.hide');
            }else {
                this.$('.day-slot').val(self.booking_data.booking_date);
                this.$('.day-slot').trigger('dp.hide');
            }
            if (!self.booking_data || !self.booking_data.booking_slot_id){
                this.$('.seat-cont').hide();
            } else {
                this.$('.seat-cont').show();
            }
            this.change_day_slot(false, this);
            // this.$('.datetimepicker').on('dp.change', function(e){ 
                
            // })

            this.$('.day-slot').on('dp.hide', function(e){
                // if(self.pos.get_order().selected_orderline.redeem_ticket){
                //     var is_booking_date_exist = self.pos.get_order().check_booking_date_redeem_ticket($(this).val())
                //     if(is_booking_date_exist){
                //         framework.unblockUI();
                //         return self.pos.gui.show_popup('confirm',{
                //             title: 'Information',
                //             body: 'Sorry, you have reached your limit to redeem the ticket!',
                //             hide_yes: true,
                //             cancel: function () {
                //                 self.gui.close_popup();
                //                 self.gui.show_popup("seat-book", {'product-id': self.pos.get_order().selected_orderline.product.id});
                //             },
                //         });
                //     }
                // }
                self.change_day_slot(e, self);
                var new_date = $(this).val();
                if (self.booking_data.booking_date != new_date){
                    $('.seat-cont').hide();
                    self.unbook_seatnumber(self.booking_data.seat_number)
                    
                }

                self.booking_data.booking_date = $(this).val();
                self.pos.get_order().selected_orderline.booking_slot_id = false
                
            })
            this.$('.date-temp').hide();
            this.$('.confirm_booking').off().click(function(){
                var good = true
                var order = self.pos.get_order()
                var line = order.selected_orderline
                var qty = line.quantity
                if (!self.booking_data.booking_slot_id){
                    $('.select-time').fadeIn('slow');
                    setTimeout(function(){ $('.select-time').fadeOut('slow') }, 3000);
                    good = false
                } 
                if (!self.booking_data.booking_date){
                    $('.select-date').fadeIn('slow');
                    setTimeout(function(){ $('.select-date').fadeOut('slow') }, 3000);
                    good = false
                } 
                if (!self.booking_data.seat_number.length > 0){
                    $('.select-seat').fadeIn('slow');
                    setTimeout(function(){ $('.select-seat').fadeOut('slow') }, 3000);
                    good = false
                } 
                if (line.is_return || line.is_exchange){
                    return self.pos.gui.close_popup();
                }
                if (good){
                    $("button[id='seat_button'][product-id="+line.get_product().id+"]").addClass('seatbook');
                    line.set_quantity(line.seat_number.length)
                    // case product bundle contains movie ticket
                    if(line.check_combo_is_booking_type()){
                        line.set_quantity(qty)
                    }
                    if(line.redeem_ticket_employee){
                        line.set_unit_price(0)
                    }
                    return self.pos.gui.close_popup();
                }
                
            })
        },
        reach_maxreturn: function(counterreturn){
            var order = this.pos.get_order();
            var line = order.selected_orderline;
            var max = Math.abs(line.get_quantity());
            if (counterreturn >= max){
                return true;
            }
            return false;
        },
        startPolling: function () {
          var timeout = 2000;
          setTimeout(this.poll.bind(this), timeout);
          this._pollCount ++;
        },
        poll: function () {
            var self = this;
            var time_id = false;
            var slot_data = self.pos.time_slot_by_id[self.booking_data.booking_slot_id]
            if (slot_data){
                time_id = slot_data.time_slot_id[0];
            }
            var product_id = false;
            if (self.booking_data.product){
                product_id = self.booking_data.product.id
            }else if(self.booking_data.product_id){
                product_id = self.booking_data.product_id[0]
            }
            if (self.booking_data){
                var booking = {
                    "booking_date": self.booking_data.booking_date,
                    "booking_slot_id": self.booking_data.booking_slot_id,
                    "time_slot_id": time_id,
                    "product_id": product_id,
                    "source": "pos",
                    "user_id": self.pos.get_cashier().user_id[0],
                    "order_reference": self.booking_data.cid
                }
                ajax.jsonRpc('/seat/poll', 'call', {'booking': booking}).then(function(data) {
                    if(data.success === true) {
                        console.log("data seat book :",data.seats)
                        self.render_seat(data.seats);
                        
                    }
                    self.startPolling();
        
                })
            }
            
        },
        // processPolledData: function (seats) {
        //     this.sc.get(seats).status('unavailable');
        // },
      });
    gui.define_popup({name:'seat-book', widget: seat_popup});
    
    screens.OrderWidget.include({
        render_orderline: function (orderline) {
            var self = this;
            try {
                var el_node = this._super(orderline);
                var el_seat_line = el_node.querySelector('#seat_button');
                var el_seat_line_bundles = el_node.querySelectorAll('#seat_button_bundle');
                var line = self.pos.get_order().selected_orderline;
                if (el_seat_line) {
                    el_seat_line.addEventListener('click', (function (btn) {
                        var order = self.pos.get_order(this);
                        if (order) {
                            return self.gui.show_popup("seat-book", {'product-id': $(btn.target).attr('product-id') , 'seat_type':'line'});
                        }
                    }.bind(this)));
                }
                if (el_seat_line_bundles){
                    for (var el_seat_line_bundle of el_seat_line_bundles) {
                        el_seat_line_bundle.addEventListener('click', (function (btn) {
                            var order = self.pos.get_order(this);
                            if (order) {
                                return self.gui.show_popup("seat-book", {'product-id': $(btn.target).attr('product-id'),'seat_type':'bundle','combo_item_index':$(btn.target).attr('index')});
                            }
                        }.bind(this)));
                    } 
                }
                return el_node;
            } catch (e) {
                console.log("failed to load orderlines make sure the product loaded on POS: ",e)
                return
            }
            
           
            
        }
    
    
    })
    return {
        'seat_popup':seat_popup
    }
})
