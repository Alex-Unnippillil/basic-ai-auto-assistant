"""Helpers for mouse interactions during quizzes.

This module exposes :class:`Clicker`, a small utility that clicks one of the
multiple‑choice answer options on screen.
"""

from __future__ import annotations

from typing import Tuple

try:  # pragma: no cover - optional heavy dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore[assignment]


class Clicker:
    """Click answer options based on a starting coordinate.

    Parameters
    ----------
    base:
        ``(x, y)`` coordinates of the first option on screen.
    offset:
        Vertical distance in pixels between consecutive options.  Defaults to
        ``40`` which suits the reference quiz layout.

    Raises
    ------
    RuntimeError
        If :mod:`pyautogui` is not available.
    """

    def __init__(self, base: Tuple[int, int], offset: int = 40) -> None:
        if pyautogui is None or not hasattr(pyautogui, "moveTo") or not hasattr(
            pyautogui, "click"
        ):
            raise RuntimeError("pyautogui not available")
        self.base = base
        self.offset = offset

    def click(self, index: int) -> None:
        """Click the option at ``index``.

        Parameters
        ----------
        index:
            Zero-based index of the option to click.
        """

        x, y = self.base
        pyautogui.moveTo(x, y + index * self.offset)
        pyautogui.click()
