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
        return [(x.id, f"{x.name} {x.key} {x.version}") for x in porcesses]

    name = fields.Char(string="Name")
    refreence = fields.Selection(string="refreence", selection=_get_processes)
    desc_xml = fields.Text(string="description xml")

    @api.onchange("refreence")
    def onchange_refreence(self):
        client = self.get_client()
        if self.refreence:
            self.desc_xml = json.dumps(
                {
                    "src_xml": client.get_xml(self.refreence),
                    "start_form_variables": client.get_start_form_variables(
                        self.refreence
                    ),
                }
            )
        else:
            self.desc_xml = ""

    @api.model
    def get_data(self):
        return self.desc_xml

    def get_properties(self, task_definition_key):
        self.ensure_one()
        return (
            json.loads(self.desc_xml).get("properties", {}).get(task_definition_key, {})
        )

    def get_inputLabels(self, task_definition_key):
        self.ensure_one()
        return (
            json.loads(self.desc_xml)
            .get("inputLabels", {})
            .get(task_definition_key, {})
        )

    def get_formLabels(self, task_definition_key):
        self.ensure_one()
        return (
            json.loads(self.desc_xml).get("formLabels", {}).get(task_definition_key, {})
        )

    def get_formTypes(self, task_definition_key):
        self.ensure_one()
        return (
            json.loads(self.desc_xml).get("formTypes", {}).get(task_definition_key, {})
        )

    def get_start_form_variables(self):
        self.ensure_one()
        data = json.loads(self.desc_xml).get("start_form_variables", {})
        return json.dumps(data)
