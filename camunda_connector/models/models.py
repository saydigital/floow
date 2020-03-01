# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from .api_clinet import Camunda


class ProcessDefinition(models.Model):
    _name = "camunda_connector.process.definition"
    _description = "The Definition of the business process"

    def get_client(self):
        client = Camunda(host="172.18.0.1", port="8080")
        return client

    def _get_processes(self):
        client = self.get_client()
        porcesses = client.processes()
        return [(x.key, x.name) for x in porcesses]

    name = fields.Char(string="Name")
    refreence = fields.Selection(string="refreence", selection=_get_processes)
    desc_xml = fields.Text(string="description xml")

    @api.onchange("refreence")
    def onchange_refreence(self):
        client = self.get_client()
        if self.refreence:
            self.desc_xml = json.dumps({"src_xml": client.get_xml(self.refreence)})
        else:
            self.desc_xml = ""

    @api.model
    def get_data(self):
        return self.desc_xml
