/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* @License       : https://store.webkul.com/license.html */

odoo.define('movie_booking_system.countdown', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var publicWidget = require('web.public.widget');
    var session = require('web.session');
    var rpc = require('web.rpc');
    
    publicWidget.registry.Countdown = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        start: function() {
            var self = this;
            var interval = setInterval(function(){
                var user_id = $('.user_id').data('id')
                var sale_order = $('.website_sale_order').data('id');
                var write_date = $('table .website_sale_order_update').data('sale-write-date');
                var config_time = $('.website_sale_order_update').data('config-time');
                var is_membership = $('.website_sale_order_is_membership').data('is_membership');
                if (!write_date){
                    var write_date = $('.website_sale_order_update').data('sale-write-date');
                }
                if (!sale_order || is_membership){
                    return
                }
                var endTime = new Date(write_date);
                endTime.setMinutes(endTime.getMinutes()+config_time)
                endTime = (Date.parse(endTime) / 1000);
                var user_timezone = new Date().getTimezoneOffset()/60;
                var now = new Date();
                now.setHours(now.getHours()+user_timezone);
                
                now = (Date.parse(now) / 1000);

                var timeLeft = endTime - now;
                if (isNaN(endTime)){
                    return;
                }
                if (timeLeft<0){
                    return
                }
                console.log("timeLeft ==",timeLeft)
                var days = Math.floor(timeLeft / 86400); 
                var hours = Math.floor((timeLeft - (days * 86400)) / 3600);
                var minutes = Math.floor((timeLeft - (days * 86400) - (hours * 3600 )) / 60);
                var seconds = Math.floor((timeLeft - (days * 86400) - (hours * 3600) - (minutes * 60)));
    
                if (hours < "10") { hours = "0" + hours; }
                if (minutes < "10") { minutes = "0" + minutes; }
                if (seconds < "10") { seconds = "0" + seconds; }
                if((days == 0 && hours == 0 && minutes == 0 && seconds == 0) || days < 0){
                    $("#countdowntimer").html('EXPIRED');
                    
                    ajax.jsonRpc("/action_get_write_date_order", 'call',{
                        'sale_order' : sale_order,
                    })
                    .then(function (result) {
                        location.reload();
                    })
                    
                }else{
                    $("#countdowntimer").html('Time Left : ' + minutes + ':' + seconds);
                }
                // ajax.jsonRpc("/action_get_write_date_order", 'call',{
                //     'sale_order' : sale_order,
                // })
                // .then(function (result) {
                //     if(!result){
                //     }else{
                //         var write_date = result.write_date
                //         var endTime = new Date(write_date);
                //         endTime = (Date.parse(endTime) / 1000);

                //         var now = new Date(result.current_time);
                //         now = (Date.parse(now) / 1000);

                //         var timeLeft = endTime - now;

                //         var days = Math.floor(timeLeft / 86400); 
                //         var hours = Math.floor((timeLeft - (days * 86400)) / 3600);
                //         var minutes = Math.floor((timeLeft - (days * 86400) - (hours * 3600 )) / 60);
                //         var seconds = Math.floor((timeLeft - (days * 86400) - (hours * 3600) - (minutes * 60)));
            
                //         if (hours < "10") { hours = "0" + hours; }
                //         if (minutes < "10") { minutes = "0" + minutes; }
                //         if (seconds < "10") { seconds = "0" + seconds; }
                //         if((days == 0 && hours == 0 && minutes == 0 && seconds == 0) || days < 0){
                //             $("#countdowntimer").html('EXPIRED');
                //             location.reload();
                //         }else{
                //             $("#countdowntimer").html(hours+ ':' + minutes + ':' + seconds);
                //         }
                //     }
                // });
                
            },1000)
            var res = this._super.apply(this, arguments);
            return res
        },
    }); 
});
