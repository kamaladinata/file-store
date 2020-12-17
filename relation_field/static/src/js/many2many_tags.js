odoo.define('relation_field.many2many_tags', function (require) {
    "use strict";

    var relational_fields = require('web.relational_fields');
    var field_registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var dialogs = require('web.view_dialogs');
    var core = require('web.core');

    var _t = core._t;
    var qweb = core.qweb;

    relational_fields.FormFieldMany2ManyTags.include({
        events: _.extend({}, AbstractField.prototype.events, {
            'click .badge': '_onBadgeTag',
        }),
        get_badge_id: function(el){
            if ($(el).hasClass('badge')) return $(el).data('id');
            return $(el).closest('.badge').data('id');
        },
        _onBadgeTag: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var self = this;
            var record_id = this.get_badge_id(event.target);
            // if (self.field.relation == "distribution.plan.box.list.size") {
            new dialogs.FormViewDialog(self, {
                res_model: self.field.relation,
                res_id: record_id,
                context: self.record.context,
                title: _t('Open: ') + self.recordData.string,
            }).on('write_completed', self, function() {
                self.dataset.cache[record_id].from_read = {};
                self.dataset.evict_record(record_id);
                self.render_value();
            }).open();
            self._renderEdit();
            // }
        },
    });

    field_registry
        .add('many2many_tags', relational_fields.FormFieldMany2ManyTags)
});