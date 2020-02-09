# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .api_clinet import Camunda


class ProcessDefinition(models.Model):
    _name = 'camunda_connector.process.definition'
    _description = 'The Definition of the business process'

    client = Camunda(host='172.18.0.2', port='8080')

    def _get_processes(self):
        porcesses = self.client.processes()
        return [(x.key, x.name) for x in porcesses]

    name = fields.Char(string='Name')
    refreence = fields.Selection(string='refreence', selection=_get_processes)
    desc_xml = fields.Text(string='description xml')

    @api.onchange('refreence')
    def onchange_refreence(self):
        if self.refreence:
            self.desc_xml = self.client.get_xml(self.refreence)
        else:
            self.desc_xml = ''
