odoo.define('ifs_bpm.view_registry', function (require) {
	"use strict";
	
	var viewRegistry = require('web.view_registry');
	var ifsBPMGraph = require('ifs_bpm.GraphView');
	var ifsBPMPivot = require('ifs_bpm.PivotView');
	
	viewRegistry.add('graph',ifsBPMGraph);
	viewRegistry.add('pivot',ifsBPMPivot);
})