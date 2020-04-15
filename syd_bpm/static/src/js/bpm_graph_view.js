odoo.define('ifs_bpm.GraphView', function(require){
	"use strict";
	
	var core = require('web.core');
	var graph = require('web.GraphView');
	
	var GraphView = graph.extend({
		
		init: function (viewInfo, params) {
			this._super.apply(this,arguments);
			
			//removes graph measures not declared in xml view 
			//from measures dropdown menu
			if(viewInfo.name === "ifs_bpm.tasks_report.graph"){
				for(var measure in this.controllerParams.measures){
					if(this.fields[measure] && !viewInfo.viewFields[measure]){
						delete this.controllerParams.measures[measure];
					}
				}								
			}
		}
	});

	return GraphView;
})