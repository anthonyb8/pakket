import requests


class RequestsClient:
    def __init__(self):
        self.url = "http://127.0.0.1:1234"

    def get(self, id: int) -> dict:
        url = f"{self.url}/demo/{id}"
        response = requests.get(url)
        return response.json()

    def post(self, data: dict) -> dict:
        url = f"{self.url}/demo"
        response = requests.post(url, json=data)
        return response.json()

    def put(self, id: int, data: dict) -> dict:
        url = f"{self.url}/demo/{id}"
        response = requests.put(url, json=data)
        return response.json()

    def delete(self, id: int) -> dict:
        id = 1
        url = f"{self.url}/demo/{id}"
        response = requests.delete(url)
        return response.json()


if __name__ == "__main__":
    client = RequestsClient()

    # Data
    id = 1
    body = {
        "model": {
            "id": 1,
            "name": "test",
            "other": ["a", "b"],
            "otherstuff": {"a": 1, "b": 2},
            "temp": 1,
        }
    }

    # Get
    response = client.get(id)
    assert response["status"] == "ok"
    assert response["data"] == "You got ID :1 "

    # Post
    response = client.post(body)
    assert response["status"] == "ok"
    assert (
        response["data"]
        == "You created instance id: 1, name: test,other: ['a', 'b'], otherstuff: {'a': 1, 'b': 2}, temp: 1"
    )

    # PUt
    response = client.put(id, body)
    assert response["status"] == "ok"
    assert (
        response["data"]
        == "You Updated instance id: 1, id: 1, name: test,other: ['a', 'b'], otherstuff: {'a': 1, 'b': 2}, temp: 1"
    )

    # Delete
    response = client.delete(id)
    assert response["status"] == "ok"
    assert response["data"] == "You deleted ID :1 "
