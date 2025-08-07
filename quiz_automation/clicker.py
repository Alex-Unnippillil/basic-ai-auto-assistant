"""Mouse automation helpers using pyautogui."""
from __future__ import annotations

try:  # pragma: no cover - optional dependency
    import pyautogui
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod
        def moveTo(x, y):
            pass

        @staticmethod
        def click():
            pass


def click_option(base: tuple[int, int], index: int, offset: int = 40) -> None:
    """Click the option at *index* relative to *base* coordinates."""
    x, y = base
    pyautogui.moveTo(x, y + index * offset)
    pyautogui.click()
