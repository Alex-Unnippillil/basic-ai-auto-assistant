import pytest

from quiz_automation import automation, chatgpt_client


def test_click_option_uses_offset(monkeypatch):
    """click_option should offset the click based on the index."""
    coords = {}

    def fake_click(x, y):
        coords["pt"] = (x, y)

    monkeypatch.setattr(automation.pyautogui, "click", fake_click)
    automation.click_option((100, 200), 2, offset=30)
    assert coords["pt"] == (100, 200 + 2 * 30)


def test_answer_question_retries_on_timeout(monkeypatch):
    """answer_question_via_chatgpt should retry when reading times out."""
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: "img")
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "Q?")
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(chatgpt_client, "OpenAI", lambda api_key=None: object())

    calls = {"read": 0}

    def fake_read(region, timeout=20.0):
        calls["read"] += 1
        if calls["read"] < 2:
            raise TimeoutError("no response")
        return "Answer A"

    monkeypatch.setattr(automation, "read_chatgpt_response", fake_read)

    clicked = {}

    def fake_click(base, idx, offset=40):
        clicked["idx"] = idx

    monkeypatch.setattr(automation, "click_option", fake_click)
    result = automation.answer_question_via_chatgpt(
        (0, 0, 10, 10), (0, 0), (0, 0, 10, 10), ["A", "B", "C", "D"], (0, 0)
    )
    assert result == "A"
    assert calls["read"] == 2
    assert clicked["idx"] == 0


def test_answer_question_fails_after_retries(monkeypatch):
    """When all retries fail, an error should be raised."""
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: "img")
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "Q?")
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(automation, "click_option", lambda base, idx, offset=40: None)

    def always_timeout(region, timeout=20.0):
        raise TimeoutError("no response")

    monkeypatch.setattr(automation, "read_chatgpt_response", always_timeout)
    with pytest.raises(TimeoutError):
        automation.answer_question_via_chatgpt(
            (0, 0, 10, 10), (0, 0), (0, 0, 10, 10), ["A", "B"], (0, 0)
        )


def test_chatgpt_timeout_retry(monkeypatch):
    """ChatGPTClient should retry and raise after repeated timeouts."""
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    class FailingOpenAI:
        def __init__(self, api_key=None):
            pass

        class responses:  # type: ignore
            @staticmethod
            def create(**kwargs):
                raise TimeoutError("boom")

    monkeypatch.setattr(chatgpt_client, "OpenAI", FailingOpenAI)
    client = chatgpt_client.ChatGPTClient()
    with pytest.raises(RuntimeError):
        client.ask("Q?", retries=2)

