import pytest

from quiz_automation import chatgpt_client
from quiz_automation.chatgpt_client import ChatGPTClient


class DummyOpenAI:
    def __init__(self, api_key=None):
        pass

    class responses:  # type: ignore
        @staticmethod
        def create(**kwargs):
            class R:
                output_text = ""
            return R()


def test_chatgpt_client_parses_json_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)
    client = ChatGPTClient()
    monkeypatch.setattr(client, "_completion", lambda prompt: '{"answer":"C"}')
    assert client.ask("Q?") == "C"


def test_chatgpt_client_retries_on_api_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)

    class APIError(Exception):
        pass

    monkeypatch.setattr(chatgpt_client, "APIError", APIError)

    client = ChatGPTClient()
    calls = {"n": 0}

    def fake(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise APIError("boom")
        return '{"answer":"A"}'

    monkeypatch.setattr(client, "_completion", fake)
    monkeypatch.setattr("quiz_automation.chatgpt_client.time.sleep", lambda s: None)
    assert client.ask("Q?") == "A"
    assert calls["n"] == 2


def test_chatgpt_client_allows_custom_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    class ModelOpenAI:
        def __init__(self, api_key=None):
            pass

        class responses:  # type: ignore
            called = {}

            @staticmethod
            def create(**kwargs):
                ModelOpenAI.responses.called = kwargs
                class R:
                    output_text = '{"answer":"B"}'
                return R()

    monkeypatch.setattr(chatgpt_client, "OpenAI", ModelOpenAI)
    client = ChatGPTClient(model="gpt-test")
    assert client.ask("Q?") == "B"
    assert ModelOpenAI.responses.called["model"] == "gpt-test"


def test_chatgpt_client_logs_and_raises_after_retries(monkeypatch, caplog):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(chatgpt_client, "OpenAI", DummyOpenAI)

    class APIError(Exception):
        pass

    monkeypatch.setattr(chatgpt_client, "APIError", APIError)

    client = ChatGPTClient()

    def boom(prompt: str) -> str:
        raise APIError("fail")

    monkeypatch.setattr(client, "_completion", boom)
    monkeypatch.setattr("quiz_automation.chatgpt_client.time.sleep", lambda s: None)

    with caplog.at_level("WARNING"):
        with pytest.raises(RuntimeError):
            client.ask("Q?", retries=2)

    assert "Attempt 1/2 failed" in caplog.text
    assert "All 2 attempts failed" in caplog.text
