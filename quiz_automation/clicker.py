"""High level helpers around optional :mod:`pyautogui` mouse control.

The real project relies on :mod:`pyautogui` which is not available in the
execution environment for the kata.  This module provides small wrappers that
gracefully degrade when the dependency is missing.  Consumers can enable a
``dry_run`` mode to silently skip real mouse interaction while keeping the
function calls intact for testing purposes.
"""

from __future__ import annotations

import time
from typing import Any

try:  # pragma: no cover - optional heavy dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore

__all__ = ["move_and_click"]


def _require_pyautogui(dry_run: bool) -> Any:
    """Return the :mod:`pyautogui` module or handle absence.

    Parameters
    ----------
    dry_run:
        When ``True`` the function returns ``None`` instead of raising a
        :class:`RuntimeError` when :mod:`pyautogui` is not importable.
    """

    if pyautogui is None or not hasattr(pyautogui, "moveTo"):
        if dry_run:
            return None
        raise RuntimeError("pyautogui not available")
    return pyautogui


def move_and_click(
    x: int,
    y: int,
    *,
    retries: int = 3,
    delay: float = 0.1,
    dry_run: bool = False,
) -> None:
    """Move the cursor to ``(x, y)`` and perform a click with retries.

    ``pyautogui`` errors are retried ``retries`` times with ``delay`` seconds
    between attempts.  If the library is missing the function either raises a
    :class:`RuntimeError` or silently returns when ``dry_run`` is ``True``.
    """

    pg = _require_pyautogui(dry_run)
    if pg is None:  # dry run with missing dependency
        return

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            pg.moveTo(x, y)
            pg.click()
            return
        except Exception as exc:  # pragma: no cover - hardware errors rare
            last_exc = exc
            if attempt >= retries:
                raise RuntimeError("move_and_click failed") from exc
            time.sleep(delay)

    if last_exc is not None:  # pragma: no cover - defensive
        raise RuntimeError("move_and_click failed") from last_exc

