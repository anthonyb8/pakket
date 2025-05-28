import requests
import json


class RequestsClient:
    def __init__(self):
        self.url = "http://127.0.0.1:1234"

    def get(self):
        url = f"{self.url}/hello"
        response = requests.get(url)

        print(response.status_code)
        print(response.text)
        print(response.json())

    def post(self):
        url = f"{self.url}/hello/1?color=blue"
        body = {"weight": 9.0}
        response = requests.post(url, json=body)

        print(response.status_code)
        print(response.text)
        print(response.json())
