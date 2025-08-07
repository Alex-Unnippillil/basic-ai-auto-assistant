"""Interactive region selection with persistent storage."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod
        def position():
            return (0, 0)


class RegionSelector:
    """Select rectangular regions and store them in a JSON file."""

    def __init__(self, path: Path = Path("regions.json")) -> None:
        self.path = path

    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively select a region and persist it under *name*."""
        input("Move mouse to top-left and press Enter...")
        x1, y1 = pyautogui.position()
        input("Move mouse to bottom-right and press Enter...")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        self.save(name, region)
        return region

    # Persistence helpers -------------------------------------------------
    def save(self, name: str, region: Tuple[int, int, int, int]) -> None:
        data = {}
        if self.path.exists():
            data = json.loads(self.path.read_text())
        data[name] = list(region)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data))

    def load(self, name: str) -> Tuple[int, int, int, int]:
        data = json.loads(self.path.read_text()) if self.path.exists() else {}
        return tuple(data[name])  # type: ignore[return-value]
