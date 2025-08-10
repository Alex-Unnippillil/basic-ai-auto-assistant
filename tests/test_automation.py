"""Tests for high level automation helpers."""

import types

import pytest

from quiz_automation import automation
from quiz_automation.stats import Stats


def test_send_to_chatgpt(monkeypatch):
    """Image should be copied and pasted using pyautogui."""

    copied = {}

    def fake_copy(img):
        copied["img"] = img

    moves = []
    hotkeys = []

    class DummyPyAuto:
        def moveTo(self, x, y):
            moves.append((x, y))

        def hotkey(self, *keys):
            hotkeys.append(keys)

    monkeypatch.setattr(automation, "copy_image_to_clipboard", fake_copy)
    monkeypatch.setattr(automation, "pyautogui", DummyPyAuto())

    automation.send_to_chatgpt("img", (10, 20))

    assert copied["img"] == "img"
    assert moves == [(10, 20)]
    assert hotkeys == [("ctrl", "v")]


def test_read_chatgpt_response_returns_text(monkeypatch):
    """OCR loop should return first non-empty response."""

    def screenshot(region):
        return "image"

    def image_to_string(img):
        return "  OK  "

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=screenshot))
    monkeypatch.setattr(automation, "pytesseract", types.SimpleNamespace(image_to_string=image_to_string))
    monkeypatch.setattr(automation.time, "sleep", lambda _: None)

    text = automation.read_chatgpt_response((0, 0, 10, 10))
    assert text == "OK"


def test_read_chatgpt_response_times_out(monkeypatch):
    """If no text is seen before timeout, a TimeoutError is raised."""

    monkeypatch.setattr(
        automation,
        "pyautogui",
        types.SimpleNamespace(screenshot=lambda region: "image"),
    )
    monkeypatch.setattr(
        automation,
        "pytesseract",
        types.SimpleNamespace(image_to_string=lambda img: ""),
    )
    times = iter([0, 0, 2])
    monkeypatch.setattr(automation.time, "time", lambda: next(times))
    monkeypatch.setattr(automation.time, "sleep", lambda _: None)

    with pytest.raises(TimeoutError):
        automation.read_chatgpt_response((0, 0, 10, 10), timeout=1.0)


def test_click_option(monkeypatch):
    """Clicking an option should move to the correct coordinate and click."""

    moves = []
    clicks = []

    class DummyPyAuto:
        def moveTo(self, x, y):
            moves.append((x, y))

        def click(self):
            clicks.append(True)

    monkeypatch.setattr(automation, "pyautogui", DummyPyAuto())

    automation.click_option((100, 200), 2, offset=30)

    assert moves == [(100, 260)]  # y + 2 * 30
    assert clicks == [True]


def test_answer_question_via_chatgpt(monkeypatch):
    """End-to-end helper should coordinate sub-functions and record stats."""

    sent = {}
    clicked = {}

    def fake_send(img, box):
        sent["args"] = (img, box)

    def fake_read(region):
        return "Letter B"

    def fake_click(base, index, offset=40):
        clicked["args"] = (base, index, offset)

    times = iter([0, 2])  # duration of 2 seconds

    monkeypatch.setattr(automation, "send_to_chatgpt", fake_send)
    monkeypatch.setattr(automation, "read_chatgpt_response", fake_read)
    monkeypatch.setattr(automation, "click_option", fake_click)
    monkeypatch.setattr(automation.time, "time", lambda: next(times))

    stats = Stats()
    letter = automation.answer_question_via_chatgpt(
        "img", (1, 2), (0, 0, 1, 1), ["A", "B", "C"], (5, 5), stats
    )

    assert letter == "B"
    assert sent["args"] == ("img", (1, 2))
    assert clicked["args"] == ((5, 5), 1, 40)
    assert stats.questions_answered == 1
    assert stats.question_times == [2]
    assert stats.token_counts == [2]  # "Letter" and "B"

