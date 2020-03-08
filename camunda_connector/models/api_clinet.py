import json
import logging

import requests

_logger = logging.getLogger(__name__)


class Camunda:
    class Process:
        def __init__(self, data):
            self.id = data["id"]
            self.key = data["key"]
            self.name = data["name"]
            self.category = data["category"]
            self.description = data["description"]
            self.version = data["version"]

        def __str__(self):
            return self.name

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get(self, endpoint, payload=None, params=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        url = f"http://{self.host}:{self.port}/engine-rest/{endpoint}"
        return self.call("get", url, payload=payload, params=params)

    def post(self, endpoint, payload=None, params=None):
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        url = f"http://{self.host}:{self.port}/engine-rest/{endpoint}"
        return self.call(
            "POST",
            url,
            headers={"Content-Type": "application/json"},
            payload=payload,
            params=params,
        )

    def call(self, method, url, headers=None, payload=None, params=None):
        if headers is None:
            headers = {}
        if payload is None:
            payload = {}
        if params is None:
            params = {}
        res = requests.request(
            method=method, headers=headers, url=url, data=payload, params=params
        )
        return res

    def processes(self):
        _logger.info("getting processes")
        data = self.get("process-definition", params={"active": "true"})
        json_data = json.loads(data.text)
        return [self.Process(rec) for rec in json_data]

    def get_xml(self, id):
        _logger.info("getting processe xml")
        data = self.get(f"process-definition/{id}/xml")
        json_data = json.loads(data.text)
        return json_data["bpmn20Xml"]

    def start_process(self, ProcessDefinitionId, businessKey, form_start_variables):
        _logger.info("start processe")
        data = self.post(
            f"process-definition/{ProcessDefinitionId}/start",
            payload=json.dumps(
                {"businessKey": businessKey, "variables": form_start_variables}
            ),
        )
        json_data = json.loads(data.text)
        return json_data["id"]

    def get_tasks(self, instance_id):
        _logger.info(f"getting tasks of {instance_id}")
        data = self.get("task", params={"processInstanceId": instance_id})
        json_data = json.loads(data.text)
        return json_data

    def get_variables(self, task_id):
        _logger.info(f"getting variables of {task_id}")
        data = self.get(f"task/{task_id}/variables")
        return json.loads(data.text)

    def get_form_variables(self, task_id):
        _logger.info(f"getting form-variables of {task_id}")
        data = self.get(f"task/{task_id}/form-variables")
        return json.loads(data.text)

    def get_start_form_variables(self, id):
        _logger.info("getting processe form-variables")
        data = self.get(f"process-definition/{id}/form-variables")
        json_data = json.loads(data.text)
        return json_data

    def task_complete(self, task_id, variables):
        _logger.info(f"complete task {task_id}")
        data = self.post(
            f"task/{task_id}/complete", payload=json.dumps({"variables": variables})
        )
        return data
