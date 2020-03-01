from odoo import api, fields, models
from ..models.api_clinet import Camunda


class ModuleName(models.TransientModel):
    _name = "camunda_connector.process.start"
    _description = "Start a new process"

    definition_id = fields.Many2one(
        comodel_name="camunda_connector.process.definition", string="Process Definition"
    )
    instance_data = fields.Text(string="instance_data")

    def get_client(self):
        client = Camunda(host="172.18.0.1", port="8080")
        return client

    def start(self):
        new_id = self.env["process.instance"].create(
            {"definition_id": self.definition_id.id}
        )
        client = self.get_client()
        new_id.instance_data = client.start_process(
            self.definition_id.refreence, new_id.name
        )
