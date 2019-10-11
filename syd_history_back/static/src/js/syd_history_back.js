odoo.define('ifs.history_back', function(require){
	"use strict";
	
	var core = require('web.core');

	core.action_registry.add("history_back", function (parent){
	    parent.trigger_up('history_back');
	});
})