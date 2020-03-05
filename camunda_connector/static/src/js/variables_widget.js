odoo.define('camunda_connector.variables_widget', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
var VariablesWidget = AbstractField.extend({
    events: {
        'change .vars_input': '_on_variables_template_change',
    },
    _render: function () {
        this.variables = JSON.parse(this.value);
        this.content = {vars:this.variables};
        console.log(this);
        this.content.disabled = false;
        if (this.mode == 'readonly'){
            this.content.disabled = true;
        }
        this.$el.html($(core.qweb.render("camunda_connector.variables_template", {widget: this.content})));

    },
    _on_variables_template_change: function (ev) {
        var $chagedVariable = $(ev.currentTarget);
        console.log($chagedVariable);
        this.variables[$chagedVariable.attr("name")].value = $chagedVariable.val();
        return this._setValue(JSON.stringify(this.variables));

    },
});

//camunda_connector.variables_widget
var fieldRegistry = require('web.field_registry');

fieldRegistry.add('variables_widget', VariablesWidget);
return {
    VariablesWidget: VariablesWidget,
};

});