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


def test_read_chatgpt_response_success(monkeypatch):
    """Return OCR text once non-empty."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=lambda region: "img"))
    monkeypatch.setattr(automation, "pytesseract", types.SimpleNamespace(image_to_string=lambda img: " hello "))
    monkeypatch.setattr(automation, "validate_region", lambda region: None)

    text = automation.read_chatgpt_response((0, 0, 1, 1), timeout=0.1)
    assert text == "hello"


def test_read_chatgpt_response_timeout(monkeypatch):
    """If no text appears before timeout a ``TimeoutError`` is raised."""

    monkeypatch.setattr(automation, "pyautogui", types.SimpleNamespace(screenshot=lambda region: "img"))
    monkeypatch.setattr(automation, "pytesseract", types.SimpleNamespace(image_to_string=lambda img: ""))
    monkeypatch.setattr(automation, "validate_region", lambda region: None)
    monkeypatch.setattr(automation, "time", types.SimpleNamespace(time=iter([0, 0.6, 1.2]).__next__, sleep=lambda _: None))

    with pytest.raises(TimeoutError):
        automation.read_chatgpt_response((0, 0, 1, 1), timeout=1.0)


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


def test_answer_question_defaults_to_a(monkeypatch):
    """When no letter A-D is found the first option is chosen."""

    clicks = []
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation, "read_chatgpt_response", lambda region, timeout=20.0: "zzz"
    )

    def fake_click(base, index, offset=40):
        clicks.append(index)

    monkeypatch.setattr(automation, "click_option", fake_click)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 0, 0), ["A", "B", "C", "D"], (10, 10)
    )

    assert letter == "A"
    assert clicks == [0]

