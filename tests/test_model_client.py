from quiz_automation.model_client import LocalModelClient
from quiz_automation.chatgpt_client import ChatGPTClient
import quiz_automation.chatgpt_client as chatgpt_client
from quiz_automation.model_protocol import ModelClientProtocol


class DummyOpenAI:
    """Minimal stand in for the OpenAI client used in tests."""

    def __init__(self, api_key=None):
        pass

    class responses:  # type: ignore
        @staticmethod
        def create(**kwargs):
            class R:
                output_text = '{"answer":"B"}'

            return R()


def test_model_client_overlap():
    client = LocalModelClient()
    question = "Which fruit is often used in cherry pie?"
    options = ["Banana", "Cherry", "Pumpkin"]
    assert client.ask(question, options) == "B"


def test_chatgpt_client_conforms(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    client = ChatGPTClient()
    assert isinstance(client, ModelClientProtocol)
    assert client.ask("Q?", ["A", "B"]) == "B"
