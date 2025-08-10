"""Utilities for interactively selecting and storing screen regions.

The real project allows a user to mark regions of the screen (e.g. the quiz
area or where answer options are located) and persists those values to disk so
they can be reused in subsequent sessions.  The implementation here keeps the
logic intentionally lightweight so unit tests can exercise the persistence
layer without needing an actual GUI environment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

try:  # pragma: no cover - optional dependency in tests
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - headless fallback
    class _DummyPyAutoGUI:
        def position(self) -> Tuple[int, int]:
            return (0, 0)

    pyautogui = _DummyPyAutoGUI()  # type: ignore


Region = Tuple[int, int, int, int]


class RegionSelector:
    """Interactively select and persist named screen regions."""

    def __init__(self, store_path: Path) -> None:
        self.store_path = Path(store_path)
        self._regions: Dict[str, Region] = {}
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                # JSON stores lists; convert to tuples for type safety
                self._regions = {k: tuple(v) for k, v in data.items()}
            except Exception:  # pragma: no cover - corrupt file
                self._regions = {}

    def save(self) -> None:
        """Persist the currently known regions to ``store_path``."""

        data = {k: list(v) for k, v in self._regions.items()}
        self.store_path.write_text(json.dumps(data))

    def load(self, name: str) -> Region:
        """Return the stored region *name*.

        Raises ``KeyError`` if the region has not previously been saved.
        """

        region = self._regions[name]
        return region

    def select(self, name: str) -> Region:
        """Prompt the user to select *name* by moving the mouse."""

        print(f"Move mouse to top-left of {name} and press Enter")
        input()
        x1, y1 = pyautogui.position()
        print(f"Move mouse to bottom-right of {name} and press Enter")
        input()
        x2, y2 = pyautogui.position()
        region: Region = (x1, y1, x2 - x1, y2 - y1)
        self._regions[name] = region
        self.save()
        return region


__all__ = ["RegionSelector", "Region"]

