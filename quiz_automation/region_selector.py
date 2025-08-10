"""Utilities for interactively selecting screen regions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

try:  # pragma: no cover - optional GUI dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(position=lambda: (0, 0))

from .utils import validate_region


class RegionSelector:
    """Persist user defined screen regions to a JSON file.

    The real application would likely provide a GUI for region selection.  For
    testing purposes we simply ask the user to position the mouse cursor at two
    corners of the desired region and press ``Enter`` after each move.
    """

    def __init__(self, storage: Path) -> None:
        self.storage = Path(storage)
        self._coords: Dict[str, Tuple[int, int, int, int]] = {}
        if self.storage.exists():
            try:
                data = json.loads(self.storage.read_text())
                for k, v in data.items():
                    self._coords[k] = tuple(v)  # type: ignore[arg-type]
            except Exception:
                self._coords = {}

    # ------------------------------------------------------------------
    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively gather two points and store the resulting region."""

        input("Move cursor to top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move cursor to bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        validate_region(region)
        self._coords[name] = region
        self.storage.write_text(json.dumps(self._coords))
        return region

    # ------------------------------------------------------------------
    def load(self, name: str) -> Tuple[int, int, int, int] | None:
        """Return a previously stored region or ``None`` if missing."""

        return self._coords.get(name)
