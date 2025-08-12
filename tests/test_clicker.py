import types

import pytest

from quiz_automation import clicker


def test_move_and_click_dry_run(monkeypatch):
    """When pyautogui is missing dry_run=True suppresses errors."""

    monkeypatch.setattr(clicker, "pyautogui", None)
    clicker.move_and_click(10, 10, dry_run=True)  # should not raise


def test_move_and_click_missing_pyautogui(monkeypatch):
    """Missing pyautogui without dry_run should raise RuntimeError."""

    monkeypatch.setattr(clicker, "pyautogui", None)
    with pytest.raises(RuntimeError):
        clicker.move_and_click(5, 5)


def test_move_and_click_retries_until_success(monkeypatch):
    """The helper retries failed clicks before succeeding."""

    calls = {"move": 0, "click": 0}

    def move_to(x, y):
        calls["move"] += 1

    def click():
        calls["click"] += 1
        if calls["click"] < 2:
            raise ValueError("boom")

    fake_pg = types.SimpleNamespace(moveTo=move_to, click=click)
    monkeypatch.setattr(clicker, "pyautogui", fake_pg)

    clicker.move_and_click(1, 2, retries=3)

    assert calls == {"move": 2, "click": 2}


def test_move_and_click_raises_after_retries(monkeypatch):
    calls = {"click": 0}

    def click():
        calls["click"] += 1
        raise ValueError("boom")

    fake_pg = types.SimpleNamespace(moveTo=lambda x, y: None, click=click)
    monkeypatch.setattr(clicker, "pyautogui", fake_pg)

    with pytest.raises(RuntimeError):
        clicker.move_and_click(1, 2, retries=2, delay=0)

    assert calls["click"] == 2

