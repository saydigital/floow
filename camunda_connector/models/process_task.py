from odoo import api, fields, models
from .api_clinet import Camunda


class ProcessTask(models.Model):
    _name = "process.task"
    _description = "Process task"

    name = fields.Char(string="Name")
    instance_id = fields.Many2one(
        comodel_name="process.instance", string="process instance"
    )
    assign_to = fields.Many2one(comodel_name="res.users", string="Assign To")
    task_id = fields.Char(string="Task ID")
    task_definition_key = fields.Char(string="Task Definition Key")

    groups_ids = fields.Many2many(comodel_name="res.groups", string="groups")
    message_text = fields.Text(string="Message Text")
