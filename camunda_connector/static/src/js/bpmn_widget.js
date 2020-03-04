odoo.define('camunda_connector.bpmn_widget', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');

    var _t = core._t;

    var BpmnWidget = AbstractField.extend({


        _on_bjs_container_change: function () {
            var self = this;
            this.bpmnViewer.saveXML({
                format: true
            }, function (err, xml) {
                if (err) {
                    return console.error('could not save BPMN 2.0 diagram', err);
                }
                var value = {
                    'src_xml': xml,
                    'properties': self.properties,
                    'definitions': self.bpmnViewer.getDefinitions()
                }
                return self._setValue(JSON.stringify(value));
            });
        },

        createTaskPanel: function (event) {
            var self = this;
            var $content = $('<div id="tabs">')
                .append(`<ul class="nav nav-tabs d-print-none" role="tablist">
                         <li class="nav-item">
                             <a href="#tabs-1" class="nav-link active" data-toggle="tab" role="tab" aria-controls="tabs-1">
                             Task Message
                             </a>
                         </li>
                         <li class="nav-item">
                             <a href="#tabs-2" class="nav-link" data-toggle="tab" role="tab" aria-controls="tabs-2">
                             Task Groups
                             </a>
                         </li>
                         <li class="nav-item">
                             <a href="#tabs-3" class="nav-link" data-toggle="tab" role="tab" aria-controls="tabs-3">
                             Task Variables
                             </a>
                         </li>
                     </ul>`)
                .append(`
                        <div class="tab-content">
                            <div id="tabs-1" role="tabpanel" class="tab-pane active">
                                <input type="html" class="o_set_txt_input" />
                            </div>
                            <div id="tabs-2" role="tabpanel" class="tab-pane fade">
                                <select id="groups_ids" multiple="multiple"/>
                            </div>
                            <div id="tabs-3" role="tabpanel" class="tab-pane fade">
                                <p> asdf</p>
                            </div>
                        </div>`);
            this.dialog = new Dialog(this, {
                size: 'extra-large',
                title: _t('Set The text'),
                buttons: [{
                    text: _t('Save'),
                    classes: 'btn-primary',
                    close: true,
                    click: function () {
                        var new_text = this.$content.find('.o_set_txt_input').val();
                        var groups = this.$content.find('#groups_ids').val();
                        self.properties[event.element.id] = {
                            'messageText': new_text,
                            'groups': groups
                        };
                        // save the values
                        self._on_bjs_container_change();
                    }
                }, {
                    text: _t('Close'),
                    close: true
                }],
                $content: $content,
            });

            this.dialog.opened().then(function () {
                document.querySelector('.modal-content').style.height = '50%';
                if(!self.properties.hasOwnProperty(event.element.id)){
                    self.properties[event.element.id] = {
                        'messageText': '',
                        'groups':''
                    };
                }
                self.dialog.$('.o_set_txt_input').val(self.properties[event.element.id].messageText);

                // load all groups
                rpc.query({
                        model: 'res.groups',
                        method: 'search',
                        args: [
                            []
                        ],
                    })
                    .then(function (result) {
                        return rpc.query({
                                model: 'res.groups',
                                method: 'read',
                                args: [result, ['name', 'category_id']],
                            })
                            .then(function (result) {
                                result = _.groupBy(result, 'category_id');
                                var options = [];
                                _.each(result, function (item) {
                                    var label = item[0].category_id[1]
                                    var sub_options = _.map(item, function (sub_item) {
                                        return {
                                            'name': sub_item.name,
                                            'value': sub_item.id,
                                            'checked': self.properties[event.element.id].groups.indexOf(sub_item.id.toString()) > -1,
                                        };
                                    });
                                    options.push({
                                        'label': label,
                                        'options': sub_options
                                    })
                                });

                                $('#groups_ids').multiselect({
                                        columns: 3,
                                        placeholder: 'Select Groups',
                                        search: true,
                                        searchOptions: {
                                            'default': 'Search Groups'
                                        }
                                    })
                                    .multiselect('loadOptions', options);
                            });
                    });



            });

            this.dialog.open();
        },
        _onElementSelected: function (event) {
            if (this.mode == 'readonly') {
                return;
            }
            var tasksRegex = /bpmn:[A-z]*Task/;
            var eventsRegex = /bpmn:[A-z]*Event/;
            if (tasksRegex.test(event.element.type)) {
                this.createTaskPanel(event);
                // show tasks properties panel
            } else if (eventsRegex.test(event.element.type)) {
                // show event properties panel

            }
        },

        _render: function () {
            var self = this;
            if (!this.value) {
                return;
            }
            self.xml_value = JSON.parse(this.value).src_xml;
            self.properties = JSON.parse(this.value).properties;
            if (self.properties === undefined){
                self.properties = {}
            }
            var content = {
                'xml_value': self.xml_value
            };

            content.mode = this.mode;
            let html = $(core.qweb.render("camunda_connector.bpmn_widget_template", {}));
            this.$el.html(html);
            this.bpmnViewer = new BpmnJS({
                container: this.$el[0].querySelector('#canvas'),
            });

            this.eventBus = this.bpmnViewer.get('eventBus');

            this.eventBus.on('element.click', this._onElementSelected.bind(this));

            this.bpmnViewer.importXML(self.xml_value, function (err) {

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
                self.$el[0].querySelector('.modeler').style.height = '100%';
                self.$el[0].querySelector('#canvas').style.height = '100%';
                self.$el[0].style.width = "100%";

                document.querySelector('.djs-palette').remove();
                document.querySelector('.djs-overlay-container').remove();
                
                // save the values
                self._on_bjs_container_change();
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