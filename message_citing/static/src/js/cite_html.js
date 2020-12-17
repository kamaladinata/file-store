odoo.define('message_citing.cite_html', function (require) {
"use strict";

    var core = require('web.core');
    var registry = require('web.field_registry');
    var rpc = require('web.rpc');

    var FieldHtml = require('web_editor.field.html');
    var dialogs = require('web.view_dialogs');

    var qweb = core.qweb;
    var _t = core._t;

    var CiteComposerHtml = FieldHtml.extend({
        events: {
            "click .open_message_citing": "_onOpenCiteMessage",
        },
        _renderEdit: function () {
            // Rewrite to render the button in composer
            var self = this;
            this._super.apply(this, arguments).then(function () {
                var composerCite = qweb.render("ComposerCite", {});
                self.$('.note-toolbar').append(composerCite);
            });
        },
        _onOpenCiteMessage: function (event) {
            // The method to open message search wizard
            var self = this;
            var resModel = this.record.data['model'];
            var resID = parseInt(this.record.data['res_id'])
            rpc.query({
                model: "mail.message",
                method: "return_message_search",
                args: [[], resModel, resID],
                context:  this.record.context,
            }).then(function (result) {
                var res = result[0],
                    cited_header = result[1];
                var context = res.context;
                var onSaved = function(record) {
                    self.$content = self.$('.note-editable:first');
                    self.$content.append(cited_header + dialog.special_message);
                    dialog.close();
                };
                var dialog = new CiteDialog(self, {
                    res_model: "cite.message",
                    title: _t("Select and cite message"),
                    context: context,
                    view_id: res.view_id,
                    readonly: false,
                    shouldSaveLocally: false,
                    on_saved: onSaved,
                    buttons: [
                        {
                            text: (_t("Close")),
                            classes: "btn-secondary o_form_button_cancel",
                            close: true,
                        },
                    ],
                });
                dialog.open();
            });
        },
    });
    var CiteDialog = dialogs.FormViewDialog.extend({
        events: {
            'click .message_cite_row': '_messageCite',
        },
        _messageCite: function(event) {
            // the method to keep the body to the composer
            event.preventDefault();
            event.stopPropagation();
            var messageId = event.currentTarget.id;
            this.special_message = messageId;
            this._save();
        },
    });

    registry.add('cite_message_composer', CiteComposerHtml);
    return CiteComposerHtml
});
