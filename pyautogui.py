"""Minimal stub of the :mod:`pyautogui` package used for testing.

The real library requires a graphical environment which is unavailable in the
execution sandbox.  Only the functions exercised by the tests are provided
here.  Each function is deliberately simple and side effect free.
"""
from __future__ import annotations

from typing import Tuple


def position() -> Tuple[int, int]:  # pragma: no cover - trivial
    return (0, 0)


def moveTo(x: int, y: int) -> None:  # pragma: no cover - trivial
    pass


def click() -> None:  # pragma: no cover - trivial
    pass


def hotkey(*keys: str) -> None:  # pragma: no cover - trivial
    pass


def press(key: str) -> None:  # pragma: no cover - trivial
    pass


def screenshot(region=None):  # pragma: no cover - simple placeholder
    return None
