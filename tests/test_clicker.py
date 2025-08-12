from types import SimpleNamespace

import pytest

from quiz_automation import clicker


def test_click_at_uses_pyautogui(monkeypatch):
    calls = []

    def fake_move(x, y):
        calls.append(("move", x, y))

    def fake_click():
        calls.append(("click",))

    monkeypatch.setattr(
        clicker,
        "pyautogui",
        SimpleNamespace(moveTo=fake_move, click=fake_click),
    )

    clicker.click_at(10, 20)

    assert calls == [("move", 10, 20), ("click",)]


def test_missing_pyautogui_attributes_raise(monkeypatch):
    monkeypatch.setattr(clicker, "pyautogui", object())

    with pytest.raises(RuntimeError):
        clicker.move_to(0, 0)

    with pytest.raises(RuntimeError):
        clicker.click()

