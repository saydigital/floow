import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.api_clinet import Camunda


class ModuleName(models.TransientModel):
    _name = "camunda_connector.process.start"
    _description = "Start a new process"

    definition_id = fields.Many2one(
        comodel_name="camunda_connector.process.definition", string="Process Definition"
    )
    form_start_variables = fields.Text(string="Form Start Variables")

    @api.onchange("definition_id")
    def onchange_definition_id(self):
        if self.definition_id:
            self.form_start_variables = self.definition_id.get_start_form_variables()

    def get_client(self):
        client = Camunda(host="172.18.0.1", port="8080")
        return client

    def start(self):
        form_start_variables = json.loads(self.form_start_variables)
        for _key, item in form_start_variables.items():
            if not item["value"]:
                raise UserError(_("You must enter the value of \n") + item["label"])
        new_id = self.env["process.instance"].create(
            {"definition_id": self.definition_id.id}
        )
        client = self.get_client()
        new_id.instance_id = client.start_process(
            self.definition_id.refreence, new_id.name, form_start_variables
        )
        new_id.get_tasks()
