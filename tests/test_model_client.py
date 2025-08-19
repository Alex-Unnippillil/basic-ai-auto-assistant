from unittest.mock import Mock

import pytest

pytest.importorskip("pydantic_settings")

import quiz_automation.model_client as mc
from quiz_automation.model_client import LocalModelClient, RemoteModelClient


def test_model_client_overlap():
    client = LocalModelClient()
    question = "Which fruit is often used in cherry pie?"
    options = ["Banana", "Cherry", "Pumpkin"]
    assert client.ask(question, options) == "B"


def test_remote_model_client(monkeypatch: pytest.MonkeyPatch) -> None:
    question = "2 + 2 = ?"
    options = ["3", "4"]
    client = RemoteModelClient(base_url="http://example.com")

    def fake_post(url, json, timeout):  # type: ignore[no-untyped-def]
        assert url == "http://example.com/answer"
        assert json == {"question": question, "options": options}
        resp = Mock()
        resp.json.return_value = {"letter": "B"}
        resp.text = '{"letter": "B"}'
        return resp

    monkeypatch.setattr(mc.requests, "post", fake_post)
    assert client.ask(question, options) == "B"
