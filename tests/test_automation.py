import time

import pytest

from quiz_automation import automation
from quiz_automation.stats import Stats


def test_answer_question_full_flow(monkeypatch):
    calls = {"send": 0, "read": 0, "click": 0}

    def fake_send(img, box):
        calls["send"] += 1

    def fake_read(region, timeout=20.0):
        calls["read"] += 1
        return "Answer: B"

    def fake_click(base, idx, offset=40):
        calls["click"] += 1
        assert idx == 1

    monkeypatch.setattr(automation, "send_to_chatgpt", fake_send)
    monkeypatch.setattr(automation, "read_chatgpt_response", fake_read)
    monkeypatch.setattr(automation, "click_option", fake_click)

    stats = Stats()
    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 1, 1), ["A", "B", "C"], (10, 10), stats
    )

    assert letter == "B"
    assert calls == {"send": 1, "read": 1, "click": 1}
    assert stats.questions_answered == 1
    assert stats.average_time > 0
    assert stats.average_tokens > 0


def test_read_chatgpt_response_waits_for_text(monkeypatch):
    imgs = ["", "image"]
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region: imgs.pop(0))

    responses = ["", "Final"]
    monkeypatch.setattr(
        automation.pytesseract, "image_to_string", lambda img: responses.pop(0)
    )

    # Keep time advancing so the loop runs twice
    start = time.time()
    monkeypatch.setattr(time, "time", lambda: start)

    def fake_sleep(seconds):
        nonlocal start
        start += seconds

    monkeypatch.setattr(time, "sleep", fake_sleep)

    text = automation.read_chatgpt_response((0, 0, 1, 1), timeout=1)
    assert text == "Final"
