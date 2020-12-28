odoo.define('website_drill.new_drill', function (require) {
"use strict";

var core = require('web.core');
var base = require('web_editor.base');
var Model = require('web.Model');
var website = require('website.website');
var contentMenu = require('website.contentMenu');

var _t = core._t;

contentMenu.TopBar.include({
    new_drill: function () {
        var model = new Model('baseball.drill');
        model.call('create_new', [], { context: base.get_context() }).then(function (drill) {
            document.location = '/coach/drill/' + drill + '?enable_editor=1';
        });
    },
});

});