odoo.define('quick_search.quick_search', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session')
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var rpc = require("web.rpc");


    var QuickSearch = Widget.extend({
        template:'SearchBar',
        events: {
            'keypress': '_MakeSearch',
        },
        init: function () {
            // Overwrite to pass to widget whether this user can see tasks quick search
            this.show_tasks_search = session.show_tasks_search;
            this._super.apply(this, arguments);
        },
        _MakeSearch: function (ev) {
            // The method to launch tasks actions
            var self = this;
            if (ev.which === 13) {
                var search_input = this.$el.find('#tasks_input')[0];
                var search = search_input.value;
                rpc.query({
                    model: 'project.task',
                    method: 'quick_search',
                    args: [{"search": search,}],
                }).then(function (action_id) {
                    search_input.value = "";
                    return self.do_action(action_id);
                });
            }
        },

    });

    SystrayMenu.Items.push(QuickSearch);

    return {
        QuickSearch: QuickSearch,
    };
});
