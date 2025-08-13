from quiz_automation.model_client import LocalModelClient
from quiz_automation.model_protocol import ModelClientProtocol


def test_model_client_overlap():
    client = LocalModelClient()
    question = "Which fruit is often used in cherry pie?"
    options = ["Banana", "Cherry", "Pumpkin"]
    assert client.ask(question, options) == "B"
    assert isinstance(client, ModelClientProtocol)
