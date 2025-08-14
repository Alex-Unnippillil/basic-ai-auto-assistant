import pytest

pytest.importorskip("pydantic_settings")

from quiz_automation.model_client import LocalModelClient


def test_model_client_overlap():
    client = LocalModelClient()
    question = "Which fruit is often used in cherry pie?"
    options = ["Banana", "Cherry", "Pumpkin"]
    assert client.ask(question, options) == "B"
