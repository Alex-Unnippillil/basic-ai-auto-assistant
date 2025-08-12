import types
import pytest

from quiz_automation import automation


def test_send_to_chatgpt_success(monkeypatch):
    """Image is copied and pasted at given coordinates."""

    calls = []

    def fake_copy(img):
        calls.append(("copy", img))
        return True

    def move(x, y):
        calls.append(("move", x, y))

    def hotkey(*keys):
        calls.append(("hotkey", keys))

    fake = types.SimpleNamespace(moveTo=move, hotkey=hotkey)
    monkeypatch.setattr(automation, "pyautogui", fake)
    monkeypatch.setattr(automation, "copy_image_to_clipboard", fake_copy)

    automation.send_to_chatgpt("img", (1, 2))

    assert calls == [("copy", "img"), ("move", 1, 2), ("hotkey", ("ctrl", "v"))]


def test_send_to_chatgpt_copy_failure(monkeypatch):
    """If the image cannot be copied a ``RuntimeError`` is raised."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(moveTo=lambda *a, **k: None, hotkey=lambda *a, **k: None))
    monkeypatch.setattr(automation, "copy_image_to_clipboard", lambda img: False)

    with pytest.raises(RuntimeError):
        automation.send_to_chatgpt("img", (0, 0))


def test_read_chatgpt_response_default_poll_interval(monkeypatch):
    """Default ``poll_interval`` of 0.5 seconds is used."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=lambda region: "img"))
    responses = iter(["", " hello "])
    monkeypatch.setattr(
        automation,
        "pytesseract",
        types.SimpleNamespace(image_to_string=lambda img: next(responses)),
    )
    monkeypatch.setattr(automation, "validate_region", lambda region: None)
    sleeps: list[float] = []
    monkeypatch.setattr(
        automation,
        "time",
        types.SimpleNamespace(time=lambda: 0, sleep=lambda s: sleeps.append(s)),
    )

    text = automation.read_chatgpt_response((0, 0, 1, 1))
    assert text == "hello"
    assert sleeps == [0.5]


def test_read_chatgpt_response_timeout(monkeypatch):
    """If no text appears before timeout a ``TimeoutError`` is raised."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=lambda region: "img"))
    monkeypatch.setattr(automation, "pytesseract", types.SimpleNamespace(image_to_string=lambda img: ""))
    monkeypatch.setattr(automation, "validate_region", lambda region: None)
    monkeypatch.setattr(automation, "time", types.SimpleNamespace(time=iter([0, 0.6, 1.2]).__next__, sleep=lambda _: None))

    with pytest.raises(TimeoutError):
        automation.read_chatgpt_response((0, 0, 1, 1), timeout=1.0)


def test_read_chatgpt_response_custom_poll_interval(monkeypatch):
    """A custom ``poll_interval`` is honoured."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=lambda region: "img"))
    responses = iter(["", " hello "])
    monkeypatch.setattr(
        automation,
        "pytesseract",
        types.SimpleNamespace(image_to_string=lambda img: next(responses)),
    )
    monkeypatch.setattr(automation, "validate_region", lambda region: None)
    sleeps: list[float] = []
    monkeypatch.setattr(
        automation,
        "time",
        types.SimpleNamespace(time=lambda: 0, sleep=lambda s: sleeps.append(s)),
    )

    text = automation.read_chatgpt_response((0, 0, 1, 1), poll_interval=0.1)
    assert text == "hello"
    assert sleeps == [0.1]


def test_click_option_uses_clicker(monkeypatch):
    """``click_option`` delegates to :class:`Clicker`."""

    calls: list[tuple] = []

    class FakeClicker:
        def __init__(self, base, offset):
            calls.append(("init", base, offset))

        def click_option(self, index):
            calls.append(("click_option", index))

    monkeypatch.setattr(automation, "Clicker", FakeClicker)

    automation.click_option((10, 10), 2, offset=5)

    assert calls == [("init", (10, 10), 5), ("click_option", 2)]


def test_click_option_missing_pyautogui(monkeypatch):
    """If ``pyautogui`` lacks ``moveTo`` a ``RuntimeError`` is raised."""

    from quiz_automation import clicker

    monkeypatch.setattr(clicker, "pyautogui", object())

    with pytest.raises(RuntimeError):
        automation.click_option((0, 0), 0)


def test_answer_question_fallback_to_first_option(monkeypatch):
    """If ChatGPT's response lacks A-D the first option is used."""

    calls: list[int] = []

    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation,
        "read_chatgpt_response",
        lambda region, timeout=20.0, poll_interval=0.5: "No option",
    )

    def fake_click_option(base, idx, offset=40):
        calls.append(idx)

    monkeypatch.setattr(automation, "click_option", fake_click_option)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 1, 1), ["A", "B", "C"], (0, 0)
    )

    assert letter == "A"
    assert calls == [0]


def test_answer_question_custom_poll_interval(monkeypatch):
    """``answer_question_via_chatgpt`` forwards ``poll_interval``."""

    calls: list[float] = []

    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)

    def fake_read(region, timeout=20.0, poll_interval=0.5):
        calls.append(poll_interval)
        return "Answer A"

    monkeypatch.setattr(automation, "read_chatgpt_response", fake_read)
    monkeypatch.setattr(automation, "click_option", lambda base, idx, offset=40: None)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 1, 1), ["A", "B"], (0, 0), poll_interval=0.2
    )
    assert letter == "A"
    assert calls == [0.2]

