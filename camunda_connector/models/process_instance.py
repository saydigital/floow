from odoo import _, fields, models

from .api_clinet import Camunda


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

    instance_id = fields.Text(string="Instance ID")

    tasks_ids = fields.One2many(
        comodel_name="process.task", inverse_name="instance_id", string="tasks"
    )

    def get_client(self):
        client = Camunda(host="172.18.0.1", port="8080")
        return client

    def get_groups(self, taskDefinitionKey):
        self.ensure_one()
        properties = self.definition_id.get_properties(taskDefinitionKey)
        groups = []
        for prop in properties.get("groups", []):
            try:
                group_id = self.env["res.groups"].search([("id", "=", int(prop))])
                if group_id:
                    groups.append((4, group_id.id))
            except Exception:
                pass
        return groups

    def get_message_text(self, taskDefinitionKey):
        self.ensure_one()
        properties = self.definition_id.get_properties(taskDefinitionKey)
        return properties.get("messageText", _("NO specified message!"))

    def get_tasks(self):
        client = self.get_client()
        for rec in self:
            tasks = client.get_tasks(rec.instance_id)
            for task in tasks:
                if not any(
                    self.env["process.task"].sudo().search([("name", "=", task["id"])])
                ):
                    new_task = self.env["process.task"].create(
                        {
                            "name": task["name"],
                            "task_id": task["id"],
                            "instance_id": rec.id,
                            "task_definition_key": task["taskDefinitionKey"],
                            "groups_ids": self.get_groups(task["taskDefinitionKey"]),
                            "message_text": self.get_message_text(
                                task["taskDefinitionKey"]
                            ),
                        }
                    )
                    new_task.get_variables()
                    new_task.get_form_variables()
                    new_task.create_activity()
