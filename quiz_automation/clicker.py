"""Utility for performing GUI clicks with configurable delays.

The module wraps :mod:`pyautogui` in a small, easily mockable interface so
that automated flows can be tested without invoking real GUI operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Callable, Optional, Protocol
import time


@dataclass
class Click:
    """Represents a click action.

    Attributes
    ----------
    x, y:
        Screen coordinates where the click should occur.
    delay:
        Optional delay in seconds to wait *after* performing the click.
    """

    x: int
    y: int
    delay: float = 0.0


class GuiLike(Protocol):
    """Protocol describing the minimal interface needed from pyautogui."""

    def click(self, *, x: int, y: int) -> None:  # pragma: no cover - simple protocol
        """Perform a click at the given coordinates."""


class Clicker:
    """Wrapper around :mod:`pyautogui` providing delay-aware clicks.

    Parameters
    ----------
    gui:
        Object implementing ``click(x=..., y=...)``.  Defaults to the real
        :mod:`pyautogui` module.
    sleep:
        Function used to handle delays.  Defaults to :func:`time.sleep` and is
        injected so tests can provide a no-op replacement.
    """

    def __init__(self, gui: Optional[GuiLike] = None, *, sleep: Callable[[float], None] | None = None) -> None:
        if gui is None:
            import pyautogui  # Imported lazily to ease testing on systems without a display.
            gui = pyautogui
        self._gui: GuiLike = gui
        self._sleep: Callable[[float], None] = sleep or time.sleep

    def click(self, x: int, y: int, delay: float = 0.0) -> None:
        """Click at ``(x, y)`` and optionally wait for ``delay`` seconds.

        Raises
        ------
        ValueError
            If ``delay`` is negative.
        """

        if delay < 0:
            raise ValueError("delay must be non-negative")
        self._gui.click(x=x, y=y)
        if delay:
            self._sleep(delay)

    def click_sequence(self, actions: Iterable[Click]) -> None:
        """Perform a sequence of :class:`Click` actions."""

        for action in actions:
            self.click(action.x, action.y, action.delay)


__all__ = ["Click", "Clicker"]
