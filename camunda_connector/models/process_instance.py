from odoo import api, fields, models


class ProcessInstance(models.Model):
    _name = "process.instance"
    _description = "Process Instance"

    name = fields.Char(
        string="Name",
        default=lambda self: self.env["ir.sequence"].next_by_code("process.instance"),
    )
    definition_id = fields.Many2one(
        comodel_name="camunda_connector.process.definition", string="Definition"
    )

    instance_data = fields.Text(string="instance_data")
