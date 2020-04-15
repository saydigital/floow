from odoo import api, fields, models


class Process(models.Model):
    _inherit = 'syd_bpm.process'

    bpmjs_text = fields.Text(string='bpmjs_text', default=""" <?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" id="Definitions_1kte6x1" targetNamespace="http://bpmn.io/schema/bpmn" exporter="bpmn-js (https://demo.bpmn.io)" exporterVersion="5.1.2">
  <bpmn:process id="Process_05a8qmm" isExecutable="false" />
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_05a8qmm" />
  </bpmndi:BPMNDiagram>
</bpmn:definitions> """)

    
    def load_design(self):
        self.ensure_one()
        print("..............", str(self.bpmjs_text))
        
