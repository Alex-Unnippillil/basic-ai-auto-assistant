import pytest

from quiz_automation import chatgpt_client
from quiz_automation.chatgpt_client import ChatGPTClient


class DummyOpenAI:
    def __init__(self, api_key=None):
        self.responses = self.Responses()

    class Responses:  # type: ignore
        def __init__(self) -> None:
            self.last_kwargs: dict | None = None

        def create(self, **kwargs):
            self.last_kwargs = kwargs
            class R:
                output_text = ""

            return R()


def test_chatgpt_client_parses_json_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    client = ChatGPTClient()
    monkeypatch.setattr(client, "_completion", lambda prompt: '{"answer":"C"}')
    assert client.ask("Q?") == "C"


def test_chatgpt_client_retries_on_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    client = ChatGPTClient()
    calls = {"n": 0}

    def fake(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("boom")
        return '{"answer":"A"}'

    monkeypatch.setattr(client, "_completion", fake)
    monkeypatch.setattr("quiz_automation.chatgpt_client.time.sleep", lambda s: None)
    assert client.ask("Q?") == "A"
    assert calls["n"] == 2


def test_chatgpt_client_validation_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    client = ChatGPTClient()
    calls = {"n": 0}

    def fake(prompt: str) -> str:
        calls["n"] += 1
        return '{"answer":"Z"}'

    monkeypatch.setattr(client, "_completion", fake)
    with pytest.raises(ValueError):
        client.ask("Q?")
    assert calls["n"] == 1


def test_chatgpt_client_configurable_parameters(monkeypatch):
    import importlib
    from quiz_automation import config

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OPENAI_MODEL", "model-env")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")
    importlib.reload(config)
    monkeypatch.setattr(chatgpt_client, "settings", config.Settings())
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)

    client = ChatGPTClient()
    assert client.model == "model-env"
    assert client.temperature == 0.5

    client2 = ChatGPTClient(model="model-param", temperature=0.9)
    assert client2.model == "model-param"
    assert client2.temperature == 0.9
