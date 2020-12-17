odoo.define('wesite_booking_system.pos_booking', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    models.load_fields("product.product", ["is_booking_type", "br_start_date", "br_end_date" , "blocked_date"]);
    models.load_fields("pos.config", ["advance_booking"]);
    models.load_fields("pos.order.line", ["booking_slot_id","booking_date","seat_number","barcode_order","seat_barcodes"]);
    models.load_models([
        {
            model: 'day.slot.config',
            fields: [],
            domain: [['product_id.available_in_pos', '=', true]],
            loaded: function (self, day_slots) {
                self.day_slot = day_slots;
                self.day_slot_by_id = {};
                self.day_slot_by_tmpl_id = {};
                for (var i = 0; i < day_slots.length; i++) {
                    var day_slot = day_slots[i];
                    self.day_slot_by_id[day_slot.id] = day_slot;
                }
                for (var i = 0; i < day_slots.length; i++) {
                    var day_slot = day_slots[i];
                    var tmpl_id = day_slot.product_id[0]
                    if (!self.day_slot_by_tmpl_id[tmpl_id]){
                        self.day_slot_by_tmpl_id[tmpl_id] = []
                    }
                    self.day_slot_by_tmpl_id[tmpl_id].push(day_slot)
                }
            }
        },
        {
            model: 'booking.slot',
            fields: [],
            domain: [['slot_config_id.product_id.available_in_pos', '=', true]],
            loaded: function (self, time_slots) {
                self.time_slot = time_slots;
                self.time_slot_by_id = {};
                self.time_slot_by_day_id = {};
                for (var i = 0; i < time_slots.length; i++) {
                    var time_slot = time_slots[i];
                    self.time_slot_by_id[time_slot.id] = time_slot;
                }
                for (var i = 0; i < time_slots.length; i++) {
                    var time_slot = time_slots[i];
                    var slot_id = time_slot.slot_config_id[0]
                    if (!self.time_slot_by_day_id[slot_id]){
                        self.time_slot_by_day_id[slot_id] = []
                    }
                    self.time_slot_by_day_id[slot_id].push(time_slot)
                    self.time_slot_by_day_id[slot_id] = self.time_slot_by_day_id[slot_id].sort((a, b) => (a.start_time > b.start_time) ? 1 : -1)
                   
                }
            }
        }
    ]);
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        delete_current_order: function () {
            var lines = this.get_order().get_orderlines();
            for (var i=0;i<lines.length;i++){
                var line = lines[i];
                line.unbook_seatnumber_all();
            }
            
            _super_posmodel.delete_current_order.apply(this, arguments);
            
        },
    });
    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        get_category_by_id: function (id) {
            var self = this;
            for (var i = 0; i < self.pos.product_categories.length; i++) {
                if (self.pos.product_categories[i].id == id) {
                    return self.pos.product_categories[i]
                } 
            }
        },
        get_seat_booking_detail: function(){
            var order = this;
            var lines = order.get_orderlines();
            var seat_data = [];
            var seat_html = '';
            for (var i=0;i<lines.length;i++){
                var line = lines[i];
                if (line.is_return || line.is_exchange){
                    continue;
                }
                if (line.product.is_booking_type){
                    var slot_time = this.pos.time_slot_by_id[line.booking_slot_id].display_name;
                    var book_time = line.booking_date+' '+slot_time
                    seat_data.push({
                        'name': line.product.name,
                        'seat_number': line.get_seatbook(),
                        'book_time': book_time

                    })
                    seat_html += '<br/><b>'+line.product.name+'</b><br/>'+book_time+'<br/>Seat number: '+line.get_seatbook();
                }
                else if (line.combo_items && line.combo_items.length){
                    for (var z=0;z<line.combo_items.length;z++){
                        var combo = line.combo_items[z];
                        var prod = this.pos.db.product_by_id[combo.product_id[0]];
                        if (prod.is_booking_type){
                            var slot_time = this.pos.time_slot_by_id[combo.booking_slot_id].display_name;
                            var book_time = combo.booking_date+' '+slot_time
                            seat_data.push({
                                'name': prod.name,
                                'seat_number': line.get_seatbook(combo),
                                'book_time': book_time
                            })
                            seat_html += '<br/><b>'+prod.name+'</b><br/>'+book_time+'<br/>Seat number: '+line.get_seatbook(combo);
                        }

                    }
                }
            }
            if(seat_data.length > 0){
                seat_html = '<b>Here is the movie(s) you choose: </b>'+seat_html+'<br/>'
            }
            return seat_html;


        }
    });
    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        check_combo_item_is_booking_type:function(id_product){
            var line = this
            var product = this.pos.db.product_by_id[id_product]
            if(product.is_booking_type && !line.is_exchange){
                return true
            }
        },
        unbook_seatnumber_all: function(){
            var line = this;
            var self = this;
            if (line.product.is_combo){
                var seat_combo_datas = [];
                for (var l=0;l<line.combo_items.length;l++){
                    var combo_item =line.combo_items[l];
                    if (combo_item.seat_number && combo_item.seat_number.length > 0){
                        var seat_data_combo  = {
                            'booking_date' : combo_item.booking_date,
                            'booking_slot_id': combo_item.booking_slot_id,
                            'seat_ids': combo_item.seat_number,
                            'book': false,
                            'user_id': self.pos.get_cashier().user_id[0]
                        }
                    }
                }
                seat_combo_datas.push(seat_data_combo)
                rpc.query({
                    model: 'seat.book',
                    method: 'unbook_seats',
                    args: [seat_combo_datas],
                }).then(function(){
                    for (var l=0;l<line.combo_items.length;l++){
                        var combo_item =line.combo_items[l];
                        if (combo_item.seat_number && combo_item.seat_number.length > 0){
                            combo_item.seat_number = [];
                        }
                    }
                    // line.trigger('change', line);
                    
                })    
            }
            else {
                var seat_data  = [{
                    'booking_date' : line.booking_date,
                    'booking_slot_id': line.booking_slot_id,
                    'seat_ids': line.seat_number,
                    'book': false,
                    'user_id': self.pos.get_cashier().user_id[0]
                }]
                rpc.query({
                    model: 'seat.book',
                    method: 'unbook_seats',
                    args: [seat_data],
                }).then(function(){
                    // line.seat_number = [];
                    // line.trigger('change', line);
                })
            }  
        },
        check_combo_is_booking_type: function(){
            var line = this;
            if(line.hasOwnProperty('combo_items')){
                if(line.combo_items.length > 0){
                    for(var i = 0; i < line.combo_items.length; i++){
                        var line_combo_id = line.combo_items[i].product_id[0]
                        var product = this.pos.db.product_by_id[line_combo_id]
                        if(product.is_booking_type && !line.is_exchange){
                            return true
                        }
                    }
                }
            }
            return false
        },
        get_product_combo_booking_type:function(){
            var line = this;
            if(line.hasOwnProperty('combo_items')){
                for(var i = 0; i < line.combo_items.length; i++){
                    var line_combo_id = line.combo_items[i].product_id[0]
                    var product = this.pos.db.product_by_id[line_combo_id]
                    if(product.is_booking_type && !line.is_exchange){
                        return product
                    }
                }
            }
        },
        get_product_combo_items: function(product_id){
            var line = this;
            if(line.hasOwnProperty('combo_items')){
                for(var i = 0; i < line.combo_items.length; i++){
                    var line_combo_items = line.combo_items[i]
                    var line_combo_id = line.combo_items[i].product_id[0]
                    var product = this.pos.db.product_by_id[line_combo_id]
                    if(line_combo_id == product_id){
                        return line_combo_items
                    }
                }
            }
        },
        get_seatbook: function(line=false){
            if (!line){
                line = this;
            }
            
            if (!line.seat_number || line.seat_number.length < 1){
                return '';
            }
            var seat = line.seat_number;
            if (typeof seat === 'string'){
                return seat.replace(/[\[\]&"]+/g, '').toUpperCase();
            } else {
                return JSON.stringify(seat).replace(/[\[\]&"]+/g, '').toUpperCase();
            }
        },
        check_seatbook: function (){
            var line = this;
            if (line.is_return || line.is_exchange){
                if(Math.abs(line.get_quantity()) != line.seat_number_return.length){
                    return false;
                }else {
                    return true;
                }
            }
            if (line.check_combo_is_booking_type()){
                for(var i=0;i<line.combo_items.length;i++){
                    var combo_line = line.combo_items[i];
                    var product = this.pos.db.product_by_id[combo_line.product_id[0]];
                    if (product.is_booking_type){
                        if (!combo_line.booking_date || combo_line.seat_number.length == 0 || !combo_line.booking_slot_id){
                            return false;
                        }
                    }
                }
                return true;
                
            }
            if (line.booking_date && line.seat_number.length > 0 && line.booking_slot_id){
                return true;
            }
            return false;
        },
        get_date_now: function(){
            var now = new Date();
            var timestamp = ''
            timestamp = now.getFullYear().toString().substr(-2);
            timestamp += ('0' + (now.getMonth()+1)).slice(-2);
            timestamp += ('0' + (now.getDate())).slice(-2);
            return timestamp
        },
        get_activity_type: function(){
            var line = this;
            var order = this.order;
            if (line.product.categ_id){
                var categ_id = order.get_category_by_id(line.product.categ_id[0])
                return categ_id.activity_type;
            }
            return '';
        },
        get_sequence_order: function(){
            var line = this;
            return rpc.query({
                model: 'res.config.settings',
                method: 'get_sequence_order',
            });

        },
        set_sequence_order: function(val){
            rpc.query({
                model: 'res.config.settings',
                method: 'set_sequence_order',
                val: val,
            }).then(function(result){
                return result
            });

        },
        initialize: function () {
            _super_order_line.initialize.apply(this, arguments);
            if (!this.booking_slot_id) {
                this.booking_slot_id = false;
            }
            if (!this.booking_date) {
                this.booking_date = false;
            }
            if (!this.seat_number) {
                this.seat_number = [];
            }

            if (!this.seat_number_return) {
                this.seat_number_return = [];
            }

            if (!this.seat_barcodes){
                this.seat_barcodes = []
            }
            // if (!this.barcode_order) {
            //     var line = this;
                
            //     line.get_sequence_order().then(function(result){
            //         line.sequence = result + 1
            //         function zero_pad(num,size){
            //             var s = ""+num;
            //             while (s.length < size) {
            //                 s = "0" + s;
            //             }
            //             return s;
            //         }
            //         /*set barcode value date(6 digits) + activity type (4 digits) + running number (4 digit)*/
            //         if (line.get_activity_type() == ''){
            //             console.log("please configure product activity type")
            //         }
            //         line.barcode_order = line.get_date_now() + line.get_activity_type() + zero_pad(line.sequence,4)
            //         return rpc.query({
            //             model: 'res.config.settings',
            //             method: 'set_sequence_order',
            //             args:[line.sequence],
            //         })

            //     })
                
            // }
        },
        init_from_JSON: function (json) {
            if (json.booking_slot_id) {
                this.booking_slot_id = json.booking_slot_id;
            }
            if (json.booking_date) {
                this.booking_date = json.booking_date;
            }
            if (json.seat_number) {
                this.seat_number = JSON.parse(json.seat_number);
            }
            if (json.barcode_order) {
                this.barcode_order = json.barcode_order;
            }
            _super_order_line.init_from_JSON.apply(this, arguments);
            if (json.booking_slot_line_ids){
                this.combo_items = json.booking_slot_line_ids
            }
        },
        export_as_JSON: function () {
            var json = _super_order_line.export_as_JSON.apply(this, arguments);
            if (!this.booking_slot_id) {
                this.booking_slot_id = false;
            }
            if (this.booking_slot_id) {
                json.booking_slot_id = this.booking_slot_id;
            }
            if (this.booking_date) {
                json.booking_date = this.booking_date;
            }
            if (this.seat_number) {
                json.seat_number = JSON.stringify(this.seat_number);
                if (this.is_return){
                    json.seat_number = '';
                }
                // if (this.combo_items){
                //     for (var i=0;i<this.combo_items.length;i++){
                //         this.combo_items[i].seat_number = JSON.stringify(this.combo_items[i].seat_number);
                //     }
                //     json.combo_items = this.combo_items;
                // }
            }
            if (this.seat_number_return) {
                json.seat_number_return = JSON.stringify(this.seat_number_return);
            }
            if (this.seat_barcodes) {
                json.seat_barcodes = JSON.stringify(this.seat_barcodes);
            }
            if (this.barcode_order) {
                json.barcode_order = this.barcode_order;
            }
            return json;
        },
    })


})