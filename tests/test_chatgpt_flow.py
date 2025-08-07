import pytest

from quiz_automation import automation
from quiz_automation.stats import Stats


class DummyImage:
    def save(self, buf, format="PNG"):  # pragma: no cover - simple stub
        buf.write(b"x")

def test_send_to_chatgpt(monkeypatch):
    calls = {}
    monkeypatch.setattr(automation.pyautogui, "click", lambda x, y: calls.update(click=(x, y)))
    monkeypatch.setattr(automation.pyautogui, "hotkey", lambda *k: calls.update(hotkey=k))
    monkeypatch.setattr(automation.pyautogui, "press", lambda k: calls.update(press=k))
    monkeypatch.setattr(automation, "copy_image_to_clipboard", lambda img: calls.update(copied=True))
    automation.send_to_chatgpt(DummyImage(), (10, 20))
    assert calls["click"] == (10, 20)
    assert calls["hotkey"] == ("ctrl", "v")
    assert calls["press"] == "enter"
    assert calls["copied"]

def test_read_chatgpt_response_success(monkeypatch):
    shots = iter(["i1", "i2", "i3"])
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: next(shots))
    texts = iter(["", "", "Answer C"])
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: next(texts))
    monkeypatch.setattr(automation.time, "sleep", lambda s: None)
    text = automation.read_chatgpt_response((0, 0, 1, 1), timeout=1.0, poll=0.1)
    assert text == "Answer C"

def test_read_chatgpt_response_timeout(monkeypatch):
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: "img")
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "")
    hotkeys = []
    monkeypatch.setattr(automation.pyautogui, "hotkey", lambda *k: hotkeys.append(k))
    monkeypatch.setattr(automation.time, "sleep", lambda s: None)
    text = automation.read_chatgpt_response((0, 0, 1, 1), timeout=0.2, poll=0.1)
    assert text == ""
    assert ("ctrl", "r") in hotkeys

def test_answer_question_via_chatgpt(monkeypatch):
    monkeypatch.setattr(automation, "screenshot_region", lambda region: "img")
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(automation, "read_chatgpt_response", lambda region, timeout=20.0: "C")
    clicked = {}
    monkeypatch.setattr(automation, "click_option", lambda base, idx, offset=40: clicked.setdefault("idx", idx))
    stats = Stats()
    letter = automation.answer_question_via_chatgpt((0,0,1,1), (1,2), (2,2,1,1), ["A","B","C","D"], (5,5), stats=stats)
    assert letter == "C"
    assert clicked["idx"] == 2
    assert stats.summary()["questions"] == 1


def test_answer_question_via_chatgpt_invalid_letter(monkeypatch):
    monkeypatch.setattr(automation, "screenshot_region", lambda region: "img")
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(automation, "read_chatgpt_response", lambda region, timeout=20.0: "?")
    clicked = {}
    monkeypatch.setattr(automation, "click_option", lambda base, idx, offset=40: clicked.setdefault("idx", idx))
    with pytest.raises(ValueError):
        automation.answer_question_via_chatgpt((0,0,1,1), (1,2), (2,2,1,1), ["A","B"], (5,5))
    assert not clicked
