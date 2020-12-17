odoo.define('movie_booking_system.Notification', function (require) {
    'use strict';
    
var Notification = require('web.Notification');
var Widget = require('web.Widget');

var notif = Notification.include({
    template: 'Notification',
    events: {
        'hidden.bs.toast': '_onClose',
        'click .o_notification_buttons button': '_onClickButton',
        'mouseenter': '_onMouseEnter',
        'mouseleave': '_onMouseLeave',
    },
    _autoCloseDelay: 6000,
    _animation: true,
    init: function (parent, params) {
        this._super(parent, params);
        if (this.type === 'danger' && params.scan_ticket) {
            this.file = 'merah.png'
            this.scan_ticket = true
        } else if (this.type === 'warning' && params.scan_ticket) {
            this.file = 'kuning.png'
            this.scan_ticket = true
        } else if (this.type === 'success' && params.scan_ticket) {
            this.file = 'hijau.png'
            this.scan_ticket = true
        }
    },
});

});
    