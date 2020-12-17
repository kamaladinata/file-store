odoo.define('sh_pos_access_rights.screens', function(require) {
    "use strict";
    
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    var rpc = require('web.rpc');
    var ActionManager = require('web.ActionManager');
    var Session = require('web.session');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var chrome = require('point_of_sale.chrome');
    var model_1 = models.PosModel.prototype.models;
    	
    var QWeb = core.qweb;
    var _t = core._t;

    // define overrided model to load
    chrome.UsernameWidget.include({
    	
    
    	click_username: function(){
            var self = this;
            this._super();
            this.gui.select_user({
                'security':     true,
                'current_user': this.pos.get_cashier(),
                'title':      _t('Change Cashier'),
            }).then(function(user){
                self.pos.set_cashier(user);
                self.renderElement();
                self.gui.screen_instances.products.actionpad.renderElement();
	            self.gui.screen_instances.products.numpad.renderElement();
	            self.gui.screen_instances.products.numpad.changedMode();
	            self.gui.screen_instances.products.numpad.start();
            });
        },
     });
    
    screens.ActionpadWidget.include({
    	 renderElement: function () {
             var self = this;
             this._super();
             // Enable-disable Payment Button
              if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.disable_payment_id[0]) === -1) {
            	  this.$('.pay').prop("disabled",false);
            	  this.$('.pay').removeClass("sh_disabled");
            	  
              }else{
            	  this.$('.pay').prop("disabled",true);
            	  this.$('.pay').addClass("sh_disabled");
              }
             // Enable-disable customer selection Button
             if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_select_customer[0]) === -1) {
            	 this.$('.set-customer').prop("disabled",false);
              	 this.$('.set-customer').removeClass("sh_disabled");
             }else{
            	 this.$('.set-customer').prop("disabled",true);
              	 this.$('.set-customer').addClass("sh_disabled");
             }
           
             
    	 },
    	
    });
    screens.NumpadWidget.include({
   	 renderElement: function () {
            var self = this;
            this._super();
            // Enable-disable discount Button
            if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_disable_discount[0]) === -1) {
            	this.$(".mode-button[data-mode='discount']").prop("disabled",false);
            	 this.$(".mode-button[data-mode='discount']").removeClass("sh_disabled_qty");
            }else{
            	this.$(".mode-button[data-mode='discount']").prop("disabled",true);
            	 this.$(".mode-button[data-mode='discount']").addClass("sh_disabled_qty");
            }
            // Enable-disable qty Button
            if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_disable_qty[0]) === -1) {
            	this.$(".mode-button[data-mode='quantity']").prop("disabled",false);
            	this.$(".mode-button[data-mode='quantity']").removeClass("sh_disabled_qty");
            }else{
            	this.$(".mode-button[data-mode='quantity']").prop("disabled",true);
            	this.$(".mode-button[data-mode='quantity']").addClass("sh_disabled_qty");
            }
            // Enable-disable price Button
            if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_disable_price[0]) === -1) {
            	this.$(".mode-button[data-mode='price']").prop("disabled",false);
             	 this.$(".mode-button[data-mode='price']").removeClass("sh_disabled_qty");
            	
            }else{
            	this.$(".mode-button[data-mode='price']").prop("disabled",true);
            	this.$(".mode-button[data-mode='price']").addClass("sh_disabled_qty");
            }
            // Enable-disable Plus Minus
            if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_disable_plus_minus[0]) === -1) {
            	this.$(".numpad-minus").prop("disabled",false);
             	 this.$(".numpad-minus").removeClass("sh_disabled");
            	
            }else{
            	this.$(".numpad-minus").prop("disabled",true);
            	this.$(".numpad-minus").addClass("sh_disabled");
            }
            // Enable-disable Numpad
            if (self.pos.get_cashier().groups_id.indexOf(self.pos.config.group_disable_numpad[0]) === -1) {
            	this.$(".number-char").prop("disabled",false);
             	 this.$(".number-char").removeClass("sh_disabled");
            	
            }else{
            	this.$(".number-char").prop("disabled",true);
            	this.$(".number-char").addClass("sh_disabled");
            }
            
            
   	 },
   	changedMode: function() {
        var mode = this.state.get('mode');
        
        if (this.pos.get_cashier().groups_id.indexOf(this.pos.config.group_disable_qty[0]) != -1 && this.pos.get_cashier().groups_id.indexOf(this.pos.config.group_disable_price[0]) != -1) {
        	mode = 'discount';
        	this.state.changeMode(mode);
        }
        else if (this.pos.get_cashier().groups_id.indexOf(this.pos.config.group_disable_qty[0]) != -1) {
        	mode = 'price';
        	this.state.changeMode(mode);
        }
        $('.selected-mode').removeClass('selected-mode');
        $(_.str.sprintf('.mode-button[data-mode="%s"]', mode), this.$el).addClass('selected-mode');
    },
    
   });

   
});