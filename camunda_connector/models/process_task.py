import json

from odoo import fields, models

from .api_clinet import Camunda


class ProcessTask(models.Model):
    _name = "process.task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    variables = fields.Text(string="Process Variables")
    form_variables = fields.Text(string="Task Form Variables")
    state = fields.Selection(
        string="State", selection=[("draft", "Draft"), ("completed", "Completed")]
    )

    def get_client(self):
        client = Camunda(host="172.18.0.1", port="8080")
        return client

    def get_variables(self):
        self.ensure_one()
        client = self.get_client()
        variables = client.get_variables(self.task_id)
        inputLabels = self.instance_id.definition_id.get_inputLabels(
            self.task_definition_key
        )
        new_variables = {}
        for key, item in variables.items():
            if key in inputLabels:
                item["label"] = inputLabels[key]
                new_variables[key] = item

        self.variables = json.dumps(new_variables)

    def get_form_variables(self):
        self.ensure_one()
        client = self.get_client()
        form_variables = client.get_form_variables(self.task_id)

        formLabels = self.instance_id.definition_id.get_formLabels(
            self.task_definition_key
        )
        formTypes = self.instance_id.definition_id.get_formTypes(
            self.task_definition_key
        )

        new_form_variables = {}
        for key, item in form_variables.items():
            if key in formLabels:
                item["label"] = formLabels[key]
                if formTypes[key] == "string":
                    item["type"] = "String"
                if formTypes[key] == "long":
                    item["type"] = "Integer"
                new_form_variables[key] = item

        self.form_variables = json.dumps(new_form_variables)

    def create_activity(self):
        self.ensure_one()
        for group in self.groups_ids:
            for user in group.users:
                self.env["mail.activity"].create(
                    {
                        "res_id": self.id,
                        "res_model_id": self.env["ir.model"]._get("process.task").id,
                        "activity_type_id": self.env.ref(
                            "mail.mail_activity_data_todo"
                        ).id,
                        "summary": self.message_text,
                        "user_id": user.id,
                    }
                )

    def complete(self):
        self.ensure_one()
        client = self.get_client()
        client.task_complete(self.task_id, json.loads(self.form_variables))
        self.state = "completed"
