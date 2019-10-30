odoo.define('syd_bpmnjs.bpmn', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');

    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var _t = core._t;

    var BpmnWidget = AbstractAction.extend(ControlPanelMixin, {
        template: "syd_bpmnjs.bpmn_temp",

        init: function(parent, params) {
            this._super(parent);
            var self = this;
            self.parent = parent;
            self.params = params;
        },

        start: function() {
            var self = this;
            var def;
            $('.o_control_panel').addClass('o_hidden');
            self.bpmn_js = new BpmnJS({ container: this.$el[0] });
            
            rpc.query({
                model: self.params['context']['model'],
                method: 'read',
                args: [[self.params['context']['active_id']], [self.params['context']['field']]],
            }).then(function(result){
                result = result[0];
                var bpmnxml = result[self.params['context']['field']];

                self.bpmn_js.importXML(bpmnxml, function(err) {
                    if (!err) {
                        console.log('success!');
                        self.bpmn_js.get('canvas').zoom('fit-viewport');
                    } else {
                        console.log('something went wrong:', err);
                    }
                });
            });

            var save_bpmn = this.$el[0].children[0];
            var close_bpmn = this.$el[0].children[1];
            self.addActions(save_bpmn, close_bpmn);
            return $.when(def, this._super.apply(this, arguments));
        },

        addActions: function(save_bpmn, close_bpmn) {
            var self = this;
            save_bpmn.addEventListener("click", function() {
                self.saveDiagram();
            });
            close_bpmn.addEventListener("click", function() {
                var r = confirm("Do You want to close without saving changes!");
                if (r == true) {
                    self.openOriginal();
                }
            });

        },

        saveDiagram  :function() {
            var self = this;
            var active_id = self.params['context']['active_id'];
            var field = self.params['context']['field'];
            var model = self.params['context']['model'];
            var original_action = self.params['context']['original_action'];
            
            self.bpmn_js.saveXML({ format: true }, function(err, xml) {
              var data = {}
              data[self.params['context']['field']] = xml;

              if (err) {
                return console.error('could not save BPMN 2.0 diagram', err);
              }
              console.log("........",self.bpmn_js._definitions);
              var r = confirm("Do You want to save!");
              if (r == true) {
                rpc.query({
                    model: model,
                    method: 'write',
                    args: [[active_id],data,]
                    })
                    .fail(function() {
                        alert('something wrong with the diagram');
                    })
                    .done(function () {
                        //window.location.reload();
                        self.openOriginal()
                    });
              }

              
            
            });
          },

          openOriginal : function(){
            var self = this;
            var active_id = self.params['context']['active_id'];
            var model = self.params['context']['model'];
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: model,
                res_id: active_id,
                views: [[false, 'form']],
                target: 'current'
            });
          },


    });



    core.action_registry.add('BpmnWidget', BpmnWidget);
    return {
        BpmnWidget: BpmnWidget,
    };

});