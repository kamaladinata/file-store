odoo.define('wesite_booking_system.MainMenu', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Session = require('web.session');
    
    var _t = core._t;
    
    var MainMenu = AbstractAction.extend({
        contentTemplate: 'scan_ticket',
    
        events: {
            "click .button_operations": function(){
                this.do_action('stock_barcode.stock_picking_type_action_kanban');
            },
            "click .button_simulation": function(){
                this.scan_attendance();
            },
            "click .o_scan_barcode_menu": function(){
                window.history.back()
            },
        },
        minTommss: function (minutes){
            var sign = minutes < 0 ? "-" : "";
            var min = Math.floor(Math.abs(minutes));
            var sec = Math.floor((Math.abs(minutes) * 60) % 60);
            return sign + (min < 10 ? "0" : "") + min + ":" + (sec < 10 ? "0" : "") + sec;
        },
        init: function(parent, action) {
            this._super.apply(this, arguments);
            console.log("check ----",action)
            // this.message_demo_barcodes = action.params.message_demo_barcodes;
            action.context.start_time = this.minTommss(action.context.start_time)
            var today = new Date();
            var date = today.getDate()+'/'+("0" + (today.getMonth() + 1)).slice(-2)+'/'+today.getFullYear();
            action.context.current_date = date;
            action.context.end_time = this.minTommss(action.context.end_time)
            this.attendance_count(action.context)
            this.context = action.context;
        },
    
        // willStart: function () {
        //     var self = this;
        //     return this._super.apply(this, arguments).then(function () {
        //         return Session.user_has_group('stock.group_stock_multi_locations').then(function (has_group) {
        //             self.group_stock_multi_location = has_group;
        //         });
        //     });
        // },
    
        start: function() {
            var self = this;
            console.log("check this :",self)
            core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
            return this._super().then(function() {
                if (self.message_demo_barcodes) {
                    self.setup_message_demo_barcodes();
                }
            });
        },
    
        destroy: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
            this._super();
        },
    
        setup_message_demo_barcodes: function() {
            var self = this;
            // Upon closing the message (a bootstrap alert), propose to remove it once and for all
            self.$(".message_demo_barcodes").on('close.bs.alert', function () {
                var message = _t("Do you want to permanently remove this message ?\
                    It won't appear anymore, so make sure you don't need the barcodes sheet or you have a copy.");
                var options = {
                    title: _t("Don't show this message again"),
                    size: 'medium',
                    buttons: [
                        { text: _t("Remove it"), close: true, classes: 'btn-primary', click: function() {
                            Session.rpc('/stock_barcode/rid_of_message_demo_barcodes');
                        }},
                        { text: _t("Leave it"), close: true }
                    ],
                };
                Dialog.confirm(self, message, options);
            });
        },
    
        _onBarcodeScanned: function(barcode) {
            var self = this;
            if (!$.contains(document, this.el)) {
                return;
            }
            Session.rpc('/scan_ticket/scan_from_main_menu', {
                barcode: barcode,
                val: this.context,
            }).then(function(result) {
                if (result.warning) {
                    console.log("--VA:L",result)
                    if (result.val){
                        self.attendance_count(result.val)
                    }
                    self.do_warning(result.warning,undefined,false,result.type,result.class);
                }
            });
        },
        do_warning: function (title, message, sticky,type, className) {
            console.warn(title, message);
            return this.displayNotification({
                type: type,
                title: title,
                message: message,
                sticky: sticky,
                className: className,
                scan_ticket : true,
            });
        },
        attendance_count: function(action) {
            var self = this;
            Session.rpc('/scan_ticket/attendance_count', {
                vals: action,
            }).then(function(result){
                console.log("attended count: ",result)
                if (result == 0){
                    self.$('#attend').text(0)
                } else {
                    action.attendance_count = result
                    self.$('#attend').text(result)
                    return result
                }
            })
        },
        scan_attendance: function() {
            var self = this;
            console.log('self ------',self)
            return this._rpc({
                    model: 'seat.book',
                    method: 'check_attendance',
                })
                .then(function(result) {
                    self.do_action(result);
                });
        },
    });
    
    core.action_registry.add('scan_ticket_main_menu', MainMenu);
    return {
        MainMenu: MainMenu,
    };
    
    });
    