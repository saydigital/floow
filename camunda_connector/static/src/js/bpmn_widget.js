odoo.define('camunda_connector.bpmn_widget', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');

    var _t = core._t;

    var BpmnWidget = AbstractField.extend({

        events: {
            'change .start_vars_input': '_on_start_vars_input_change',
        },

        _on_start_vars_input_change: function (ev) {
            var $effected = $(ev.currentTarget);
            this.start_form_variables[$effected.attr("name")].label = $effected.val();
            this._on_bjs_container_change();
        },


        _on_bjs_container_change: function () {
            var self = this;
            this.bpmnViewer.saveXML({
                format: true,
            }, function (err, xml) {
                if (err) {
                    return console.error('could not save BPMN 2.0 diagram', err);
                }
                var value = {
                    'src_xml': xml,
                    'start_form_variables': self.start_form_variables,
                    'properties': self.properties,
                    'definitions': self.bpmnViewer.getDefinitions(),
                    'inputLabels': self.inputLabels,
                    'formLabels': self.formLabels,
                    'formTypes': self.formTypes,
                };
                return self._setValue(JSON.stringify(value));
            });
        },

        createTaskPanel: function (event) {
            var self = this;
            var $content = $('<div id="tabs">')
                .append(`<ul class="nav nav-tabs d-print-none" role="tablist">
                         <li class="nav-item">
                             <a href="#tabs-1" class="nav-link active"
                             data-toggle="tab" role="tab" aria-controls="tabs-1">
                             Task Message
                             </a>
                         </li>
                         <li class="nav-item">
                             <a href="#tabs-2" class="nav-link" data-toggle="tab"
                             role="tab" aria-controls="tabs-2">
                             Task Groups
                             </a>
                         </li>
                         <li class="nav-item">
                             <a href="#tabs-3" class="nav-link" data-toggle="tab"
                             role="tab" aria-controls="tabs-3">
                             Task Variables
                             </a>
                         </li>
                     </ul>`);
            var $tabContent = $('<div class="tab-content">');
            var $tab1 = $('<div id="tabs-1" role="tabpanel" class="tab-pane active">');
            $tab1.append(`<label for="o_set_txt_input">Message</label>
                          <input type="html" class="o_set_txt_input"
                          name="o_set_txt_input" />`);

            var $tab2 = $(`<div id="tabs-2" role="tabpanel" class="tab-pane fade">
                                <select id="groups_ids" multiple="multiple"/>
                          </div>`);

            var $tab3 = $('<div id="tabs-3" role="tabpanel" class="tab-pane fade">');

            $tabContent.append($tab1)
                .append($tab2)
                .append($tab3);
            $content.append($tabContent);

            this.dialog = new Dialog(this, {
                size: 'extra-large',
                title: _t('Set The text'),
                buttons: [{
                    text: _t('Save'),
                    classes: 'btn-primary',
                    close: true,
                    click: function () {
                        var click_self = this;
                        var new_text = this.$content.find('.o_set_txt_input').val();
                        var groups = this.$content.find('#groups_ids').val();
                        self.properties[event.element.id] = {
                            'messageText': new_text,
                            'groups': groups,
                        };

                        Object.keys(self.inputLabels[event.element.id]).forEach(
                            function (key) {
                                var val = click_self.$content.find('#' + key).val();
                                self.inputLabels[event.element.id][key] = val;
                            });

                        // Save the values
                        self._on_bjs_container_change();
                    },
                }, {
                    text: _t('Close'),
                    close: true,
                }],
                $content: $content,
            });

            this.dialog.opened().then(function () {
                document.querySelector('.modal-content').style.height = '50%';
                if (!Object.prototype.hasOwnProperty.call(self.properties,
                    event.element.id)) {
                    self.properties[event.element.id] = {
                        'messageText': '',
                        'groups': '',
                    };
                }
                self.dialog.$('.o_set_txt_input')
                    .val(self.properties[event.element.id].messageText);

                // Load all groups
                rpc.query({
                    model: 'res.groups',
                    method: 'search',
                    args: [
                        [],
                    ],
                })
                    .then(function (result_ids) {
                        return rpc.query({
                            model: 'res.groups',
                            method: 'read',
                            args: [result_ids, ['name', 'category_id']],
                        })
                            .then(function (result_read) {
                                var result = _.groupBy(result_read, 'category_id');
                                var options = [];
                                _.each(result, function (item) {
                                    var label = item[0].category_id[1];
                                    var sub_options = _.map(item, function (sub_item) {
                                        return {
                                            'name': sub_item.name,
                                            'value': sub_item.id,
                                            'checked': self.properties[event.element.id]
                                                .groups.indexOf(
                                                    sub_item.id.toString()
                                                ) > -1,
                                        };
                                    });
                                    options.push({
                                        'label': label,
                                        'options': sub_options,
                                    });
                                });

                                $('#groups_ids').multiselect({
                                    columns: 3,
                                    placeholder: 'Select Groups',
                                    search: true,
                                    searchOptions: {
                                        'default': 'Search Groups',
                                    },
                                })
                                    .multiselect('loadOptions', options);
                            });
                    });

                if (!Object.prototype.hasOwnProperty.call(self.inputLabels,
                    event.element.id)) {
                    self.inputLabels[event.element.id] = {};
                }
                if (!Object.prototype.hasOwnProperty.call(self.formLabels,
                    event.element.id)) {
                    self.formLabels[event.element.id] = {};
                }
                if (!Object.prototype.hasOwnProperty.call(self.formTypes,
                    event.element.id)) {
                    self.formTypes[event.element.id] = {};
                }
                if (Object.prototype.hasOwnProperty.call(event.element.businessObject,
                    'extensionElements')) {
                    var values = event.element.businessObject.extensionElements.values;
                    Object.keys(values).forEach(function (key) {
                        var value = values[key];
                        if (value.$type === "camunda:inputOutput") {
                            Object.keys(value.$children).forEach(function (child) {
                                var childValue = value.$children[child];
                                if (childValue.$type === "camunda:inputParameter") {
                                    self.inputLabels[event.element.id][childValue
                                        .name] = childValue.name in self
                                        .inputLabels[event.element.id] && self
                                        .inputLabels[event.element.id][childValue
                                            .name] || '';
                                }
                            });
                        } else if (value.$type === "camunda:formData") {
                            Object.keys(value.$children).forEach(function (child) {
                                self.formLabels[event.element.id][value
                                    .$children[child].id] = value.$children[child]
                                    .label;
                                self.formTypes[event.element.id][value
                                    .$children[child].id] = value.$children[child]
                                    .type;
                            });
                        }
                    });
                }
                Object.keys(self.inputLabels[event.element.id]).forEach(function (key) {
                    self.dialog.$('#tabs-3')
                        .append('<label for="' + key + '">' + key + '</label>')
                        .append('<input id="' + key + '" name="' + key +
                        '" type="text" value="' + self.inputLabels[event
                            .element.id][key] + '"/>');
                });
            });

            this.dialog.open();
        },
        _onElementSelected: function (event) {
            if (this.mode === 'readonly') {
                return;
            }
            if (event.element.type === "bpmn:UserTask") {
                this.createTaskPanel(event);
                // Show tasks properties panel
            } else if (event.element.type === "bpmn:StartEvent") {
                // Show event properties panel

            }
        },

        _render: function () {
            var self = this;
            if (!this.value) {
                return;
            }
            self.xml_value = JSON.parse(this.value).src_xml;
            self.start_form_variables = JSON.parse(this.value).start_form_variables;
            self.properties = JSON.parse(this.value).properties;
            self.inputLabels = JSON.parse(this.value).inputLabels;
            self.formLabels = JSON.parse(this.value).formLabels;
            self.formTypes = JSON.parse(this.value).formTypes;

            if (self.properties === undefined) {
                self.properties = {};
            }
            if (self.inputLabels === undefined) {
                self.inputLabels = {};
            }
            if (self.formLabels === undefined) {
                self.formLabels = {};
            }
            if (self.formTypes === undefined) {
                self.formTypes = {};
            }

            var content = {
                'start_vars': self.start_form_variables,
                'mode': this.mode,
            };

            var html = $(core.qweb.render("camunda_connector.bpmn_widget_template",
                {widget: content}));
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
                // Access viewer components
                var canvas = self.bpmnViewer.get('canvas');
                // Zoom to fit full viewport
                canvas.zoom('fit-viewport');
                // Increase form height
                document.querySelector('.o_form_view').style.height = "100%";
                self.$el[0].style.height = '100%';
                self.$el[0].querySelector('.modeler').style.height = '100%';
                self.$el[0].querySelector('#canvas').style.height = '100%';
                self.$el[0].style.width = "100%";
                document.querySelector('.djs-palette').remove();
                document.querySelector('.djs-overlay-container').remove();
                // Save the values
                self._on_bjs_container_change();
            });
        },
    });
    var fieldRegistry = require('web.field_registry');
    fieldRegistry.add('bpmn_widget', BpmnWidget);
    return {
        BpmnWidget: BpmnWidget,
    };
});
