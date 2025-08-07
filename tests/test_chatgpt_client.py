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
