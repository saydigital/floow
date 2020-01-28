odoo.define('camunda_connector.bpmn_widget', function(require) {
    "use strict";
    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
    var BpmnWidget = AbstractField.extend({


        _on_bjs_container_change: function() {
            var self = this;
            this.bpmnViewer.saveXML({ format: true }, function(err, xml) {
                if (err) {
                    return console.error('could not save BPMN 2.0 diagram', err);
                }
                return self._setValue(xml);
            });
        },

        _onElementSelected : function(event) {
            var tasksRegex = /bpmn:[A-z]*Task/;
            var eventsRegex = /bpmn:[A-z]*Event/;
            if(tasksRegex.test(event.element.type)){
                console.log(this.elements[event.element.id]);
                // show tasks properties panel
            }
            else if(eventsRegex.test(event.element.type)){
                // show event properties panel

            }
            
            // if (self.mode !== 'readonly') {
            //     self._on_bjs_container_change();
            // }
        },

        _render: function() {
            var self = this;
            if(!this.value){
                return;
            }
            var content = { 'xml_value': this.value };
            content.mode = this.mode;
            let html = $(core.qweb.render("camunda_connector.bpmn_widget_template", { widget: content }));
            this.$el.html(html);
            this.bpmnViewer = new BpmnJS({
                container: this.$el[0].querySelector('#canvas'),
            });

            this.eventBus = this.bpmnViewer.get('eventBus');

            this.eventBus.on('element.click', this._onElementSelected.bind(this));

            this.elements = {};
            this.bpmnViewer.importXML(this.value, function(err) {

                if (err) {
                    return console.error('could not import BPMN 2.0 diagram', err);
                }

                // access viewer components
                var canvas = self.bpmnViewer.get('canvas');


                // zoom to fit full viewport
                canvas.zoom('fit-viewport');

                // increase form height
                document.querySelector('.o_form_view').style.height = "100%";

                self.$el[0].style.height = '100%';
                console.log(self.$el[0]);
                self.$el[0].querySelector('.modeler').style.height = '100%';
                self.$el[0].querySelector('#canvas').style.height = '100%';
                self.$el[0].style.width = "100%";

                document.querySelector('.djs-palette').remove();
                document.querySelector('.djs-overlay-container').remove();
                self.bpmnViewer.getDefinitions().rootElements.forEach(rootElement => {
                    rootElement.flowElements.forEach(element => {
                        self.elements[element.id] = element;
                    });
                });
            });


        },
    });


    //camunda_connector.bpmn_widget
    var fieldRegistry = require('web.field_registry');

    fieldRegistry.add('bpmn_widget', BpmnWidget);
    return {
        BpmnWidget: BpmnWidget,
    };

});