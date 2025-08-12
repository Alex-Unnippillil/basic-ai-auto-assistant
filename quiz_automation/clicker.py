"""Lightweight helpers for moving the mouse and performing clicks.

The real project uses :mod:`pyautogui` for desktop automation.  The tests in
this kata run in a minimal environment where that dependency may be missing, so
this module mirrors the graceful fallback approach used elsewhere in the
project.  When :mod:`pyautogui` cannot be imported a very small stand‑in object
provides the attributes used here which allows the functions to be imported and
monkeypatched for unit tests.
"""

from __future__ import annotations

try:  # pragma: no cover - optional heavy dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    # ``pyautogui`` is not available.  Provide a minimal mock so the rest of the
    # code can still be exercised.  Each attribute mirrors the functions used in
    # this module and can be monkeypatched in tests if required.
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(  # type: ignore[attr-defined]
        moveTo=lambda *_, **__: None,
        click=lambda *_, **__: None,
    )

__all__ = ["Clicker", "move_to", "click", "click_at"]


class Clicker:
    """Encapsulate mouse movement and clicking via :mod:`pyautogui`."""

    def move(self, x: int, y: int) -> None:
        """Move the mouse cursor to ``(x, y)``."""

        if not hasattr(pyautogui, "moveTo"):
            raise RuntimeError("pyautogui not available")
        pyautogui.moveTo(x, y)

    def click(self) -> None:
        """Perform a mouse click at the current cursor location."""

        if not hasattr(pyautogui, "click"):
            raise RuntimeError("pyautogui not available")
        pyautogui.click()

    def click_at(self, x: int, y: int) -> None:
        """Move the mouse to ``(x, y)`` and click."""

        self.move(x, y)
        self.click()


_default_clicker = Clicker()


def move_to(x: int, y: int) -> None:
    """Module level convenience wrapper for :class:`Clicker.move`."""

    _default_clicker.move(x, y)


def click() -> None:
    """Module level convenience wrapper for :class:`Clicker.click`."""

    _default_clicker.click()


def click_at(x: int, y: int) -> None:
    """Move to ``(x, y)`` and click using the default :class:`Clicker`."""

    _default_clicker.click_at(x, y)

