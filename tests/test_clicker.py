import types
import pytest

from quiz_automation import clicker


def test_click_at_moves_and_clicks(monkeypatch):
    """``Clicker.click_at`` should move to the coordinates then click."""

    calls: list[tuple] = []

    def move_to(x, y):
        calls.append(("move", x, y))

    def do_click():
        calls.append(("click",))

    fake = types.SimpleNamespace(moveTo=move_to, click=do_click)
    monkeypatch.setattr(clicker, "pyautogui", fake)

    clicker.Clicker().click_at(10, 20)

    assert calls == [("move", 10, 20), ("click",)]


def test_move_raises_when_pyautogui_missing(monkeypatch):
    """``Clicker.move`` should raise when ``pyautogui`` lacks ``moveTo``."""

    monkeypatch.setattr(clicker, "pyautogui", object())
    with pytest.raises(RuntimeError):
        clicker.Clicker().move(1, 2)


def test_click_raises_when_pyautogui_missing(monkeypatch):
    """``Clicker.click`` should raise when ``pyautogui`` lacks ``click``."""

    monkeypatch.setattr(clicker, "pyautogui", types.SimpleNamespace(moveTo=lambda *a, **k: None))
    with pytest.raises(RuntimeError):
        clicker.Clicker().click()

