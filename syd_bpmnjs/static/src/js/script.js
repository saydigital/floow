odoo.define('syd_bpmnjs.related_pro', function(require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var registry = require('web.field_registry');

    var BpmnWidget = require('syd_bpmnjs.bpmn');
    var FieldText = require('web.basic_fields').FieldText;

    var bpmnchart = FieldText.extend({

        _makebpmnjs: function() {
            return new BpmnWidget.BpmnWidget(this);
        },

        start: function() {
            var self = this;
            var def;
            self.bpmnjs = self._makebpmnjs();
            def = this.bpmnjs.appendTo('<div>').done(function() {
                self.bpmnjs.$el.addClass(self.$el.attr('class'));
                self._prepareInput(self.bpmnjs.$input);
                self._replaceElement(self.bpmnjs.$el);
            });
            return $.when(def, this._super.apply(this, arguments));
        },

        _renderReadonly: function() {
            var self = this;
            self._replaceElement(self.bpmnjs.$el);
        },

        _renderEdit: function() {
            var self = this;
            self._replaceElement(self.bpmnjs.$el);
        },

        _doDebouncedAction: function() {

        },

        // start: function () {
        //     var self = this;
        //     var def;
        //     self.bpmnjs = self._makebpmnjs();
        //     if (self.mode === 'edit') {


        //         console.log("...........self.mode", self.mode);


        //     }
        //     else if (self.mode === 'readonly') {
        //         self.bpmnjs = self._makebpmnjs();
        //         console.log("...........self.mode", self.mode);

        //     }
        //     return $.when(def, this._super.apply(this, arguments));
        // },

        // _renderEdit: function () {
        //     var self = this;
        //     self.bpmnjs.importXML(self.value, function (err) {
        //         if (!err) {
        //             console.log('success!');
        //             self.bpmnjs.get('canvas').zoom('fit-viewport');
        //         } else {
        //             console.log('something went wrong:', err);
        //         }
        //     });
        //     self.bpmnjs.saveXML(function(xml){
        //         self.$input = xml;
        //     });

        // },

        // _renderReadonly: function () {
        //     var self = this;
        //     self.bpmnjs.importXML(self.value, function (err) {
        //         if (!err) {
        //             console.log('success!');
        //             self.bpmnjs.get('svg').zoom('fit-viewport');
        //         } else {
        //             console.log('something went wrong:', err);
        //         }
        //     });
        // },


        // _render: function () {

        //     var self = this;

        //     var viewer = new BpmnJS();
        //     console.log("...................all,", self.value);
        //     // attach it to some element
        //     viewer.attachTo(self.$el[0]);

        //     viewer.importXML(self.value, function (err) {

        //         if (!err) {
        //             console.log('success!');
        //             viewer.get('canvas').zoom('fit-viewport');
        //         } else {
        //             console.log('something went wrong:', err);
        //         }
        //     });



        // },

        // _renderReadonly: function () {

        //     var self = this;

        //     var viewer = new BpmnJS();
        //     console.log("...................,", self.$el);
        //     // attach it to some element
        //     viewer.attachTo(self.$el[0]);

        //     viewer.importXML(self.value, function (err) {

        //         if (!err) {
        //             console.log('success!');
        //             viewer.get('canvas').zoom('fit-viewport');
        //         } else {
        //             console.log('something went wrong:', err);
        //         }
        //     });



        // },


        // _renderEdit: function () {
        //     var self = this;

        //     this._super.apply(this, arguments);

        //     var viewer = new BpmnJS();

        //     viewer.attachTo(self.$el[0]);

        //     viewer.importXML(self.value, function (err) {

        //         if (!err) {
        //             console.log('success!');
        //             viewer.get('canvas').zoom('fit-viewport');
        //         } else {
        //             console.log('something went wrong:', err);
        //         }
        //     });

        // },


    });

    registry.add('bpmnjs', bpmnchart);

    return {
        bpmnchart: bpmnchart,
    };

});