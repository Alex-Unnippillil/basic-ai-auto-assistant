import pytest

from quiz_automation import chatgpt_client
from quiz_automation.chatgpt_client import ChatGPTClient
from quiz_automation.config import settings


class DummyOpenAI:
    """Minimal stand in for the OpenAI client used in tests."""

    last_kwargs = None

    def __init__(self, api_key=None):
        pass

    class responses:  # type: ignore
        @staticmethod
        def create(**kwargs):
            DummyOpenAI.last_kwargs = kwargs
            class R:
                output_text = '{"answer":"B"}'
            return R()


def _setup_client(monkeypatch) -> ChatGPTClient:
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    return ChatGPTClient()


def test_chatgpt_client_parses_json_response(monkeypatch):
    client = _setup_client(monkeypatch)
    assert client.ask("Q?") == "B"


def test_chatgpt_client_uses_settings(monkeypatch):
    monkeypatch.setattr(settings, "model", "my-model")
    monkeypatch.setattr(settings, "openai_system_prompt", "my prompt")
    client = _setup_client(monkeypatch)
    client.ask("Q?")
    kwargs = DummyOpenAI.last_kwargs
    assert kwargs["model"] == "my-model"
    assert kwargs["input"][0]["content"] == "my prompt"


def test_chatgpt_client_retries_on_transient_error(monkeypatch):
    client = _setup_client(monkeypatch)
    calls = {"n": 0}

    def fake(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise TimeoutError("temporary")
        return '{"answer":"A"}'

    monkeypatch.setattr(client, "_completion", fake)
    monkeypatch.setattr("quiz_automation.chatgpt_client.time.sleep", lambda s: None)
    assert client.ask("Q?") == "A"
    assert calls["n"] == 2
