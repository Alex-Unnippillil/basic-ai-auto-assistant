from __future__ import annotations

"""Utility for interactively selecting and storing screen regions."""

import json
from pathlib import Path
from typing import Dict, Tuple

import pyautogui


class RegionSelector:
    """Persist rectangular screen regions to a JSON file.

    The selector prompts the user to position the mouse cursor at the top-left
    and bottom-right corners of the desired region.  Coordinates are persisted
    allowing later sessions to load previously selected regions.
    """

    def __init__(self, storage: Path) -> None:
        self.storage = Path(storage)
        self._regions: Dict[str, Tuple[int, int, int, int]] = {}
        if self.storage.exists():
            try:
                self._regions = json.loads(self.storage.read_text())
            except Exception:
                self._regions = {}

    # ------------------------------------------------------------------
    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively select a region and store it under *name*."""
        input("Place cursor at top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Place cursor at bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        self._regions[name] = region
        self.storage.write_text(json.dumps(self._regions))
        return region

    # ------------------------------------------------------------------
    def load(self, name: str) -> Tuple[int, int, int, int]:
        """Return the previously stored region for *name*.

        Raises ``KeyError`` if the region has not yet been selected.
        """
        region = self._regions.get(name)
        if region is None:
            raise KeyError(name)
        return tuple(region)
