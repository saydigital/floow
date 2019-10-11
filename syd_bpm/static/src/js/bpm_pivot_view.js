odoo.define('ifs_bpm.PivotView', function(require){
	"use strict";
	
	var core = require('web.core');
	var pivot = require('web.PivotView');
	
	var PivotView = pivot.extend({
		
		init: function (viewInfo, params) {
			this._super.apply(this,arguments);
			
			//removes pivot measures not declared in xml view 
			//from measures dropdown menu
			if(viewInfo.name === "ifs_bpm.tasks_report.pivot"){
				for(var measure in this.controllerParams.measures){
					if(this.fields[measure] && !viewInfo.viewFields[measure]){
						delete this.controllerParams.measures[measure];
					}
				}								
			}
		}
	});

	return PivotView;
})