import requests
import json
import logging

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

    def get(self, endpoint, payload={}, params={}):
        url = f"http://{self.host}:{self.port}/engine-rest/{endpoint}"
        return self.call("get", url, payload=payload, params=params)

    def post(self, endpoint, payload={}, params={}):
        url = f"http://{self.host}:{self.port}/engine-rest/{endpoint}"
        return self.call(
            "POST",
            url,
            headers={"Content-Type": "application/json"},
            payload=payload,
            params=params,
        )

    def call(self, method, url, headers={}, payload={}, params={}):
        res = requests.request(
            method=method, headers=headers, url=url, data=payload, params=params
        )
        return res

    def processes(self):
        _logger.info("getting processes")
        data = self.get(
            "process-definition", params={"active": "true", "latestVersion": "true"}
        )
        json_data = json.loads(data.text)
        return [self.Process(rec) for rec in json_data]

    def get_xml(self, key):
        _logger.info("getting processe xml")
        data = self.get(f"process-definition/key/{key}/xml")
        json_data = json.loads(data.text)
        return json_data["bpmn20Xml"]

    def start_process(self, ProcessDefinitionKey, businessKey):
        _logger.info("start processe")
        data = self.post(
            f"process-definition/key/{ProcessDefinitionKey}/start",
            payload=json.dumps({"businessKey": businessKey}),
        )
        return data.text
