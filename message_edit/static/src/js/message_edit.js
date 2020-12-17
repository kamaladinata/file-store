odoo.define('message_edit.message_edit', function(require) {

    var core = require('web.core');
    var data = require('web.data');
    var _t = core._t;
    var chatThread = require('mail.widget.Thread');
    var dialogs = require('web.view_dialogs');
    var mailMessage = require('mail.model.Message');
    var abstractMessage = require('mail.model.AbstractMessage');

    mailMessage.include({
        init: function (parent, data, emojis) {
            // Rewrite to add 'changed'
            this._super.apply(this, arguments);
            this._changed = data.changed;
            this.activity_feedback = data.activity_feedback;
        },
        _isAlreadyEdited: function () {
            // True in case a message has been already modified
            return this._changed;
        },
        _mightBeEdited: function (){
            // False in case it is a system notification (but not activity feedback) or contains tracking values
            var might = true;
            if (!this.activity_feedback && (this.getType() === 'notification' || this.hasTrackingValues())) {
                might = false;
            }
            return might;
        }
    });

    abstractMessage.include({
        _isAlreadyEdited: function () {
            // not to have error in create mode
            return false;
        },
        _mightBeEdited: function (){
            // not to have error in create mode
            return false;
        }
    });


    chatThread.include({
        events: _.extend({}, chatThread.prototype.events, {
            'click .fa-edit': '_onMessageEdit',
        }),

        _onMessageEdit: function (event) {
            // Method to open dialog to change message
            var self = this;
            var messageObj = $(event.currentTarget);
            var messageId = parseInt(event.target.dataset['messageId'], 10);
            var $message = messageObj.parents('.o_thread_message');
            var context = {"message_edit": true};
            this._rpc({
                model: "mail.message",
                method: 'get_edit_formview_id',
                args: [[messageId]],
                context: context,
            }).then(function (view_id) {
                var onSaved = function(record) {
                    // Since we migth be both in field of form and in chatter we can't use setValue
                    // Instead we update the body manually through the js
                    var updatedBody = record.data.body;
                    var contentElement = $message.find('.o_thread_message_content');
                    // We use indexOf, since innerHTML has a lot of breaks inside
                    if (contentElement[0].innerHTML.indexOf(updatedBody) == -1) {
                        contentElement[0].innerHTML = updatedBody;
                        messageObj.parent().addClass("already_changed");
                    };
                };
                new dialogs.FormViewDialog(self, {
                    res_model: "mail.message",
                    res_id: messageId,
                    context: context,
                    title: _t("Edit Message"),
                    view_id: view_id,
                    readonly: false,
                    on_saved: onSaved,
                    shouldSaveLocally: false,
                }).open();
            });
        },
    });

});
