"""Mouse automation helpers using pyautogui."""
from __future__ import annotations

import importlib


def _pyautogui():
    try:  # pragma: no cover - import at runtime for headless tests
        return importlib.import_module("pyautogui")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pyautogui is required for click automation") from exc


def click_option(base: tuple[int, int], index: int, offset: int = 40) -> None:
    """Click the option at *index* relative to *base* coordinates."""
    pg = _pyautogui()
    x, y = base
    pg.moveTo(x, y + index * offset)
    pg.click()
