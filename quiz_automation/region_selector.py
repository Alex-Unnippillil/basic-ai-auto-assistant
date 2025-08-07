"""Utility for interactively selecting and persisting screen regions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple, Optional

try:  # pragma: no cover - optional dependency
    import pyautogui
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod
        def position():
            return (0, 0)


class RegionSelector:
    """Persist coordinates of named screen regions to a JSON file."""

    def __init__(self, path: Path | str = "coords.json") -> None:
        self.path = Path(path)
        if self.path.exists():
            self.coords: Dict[str, Tuple[int, int, int, int]] = {
                k: tuple(v) for k, v in json.loads(self.path.read_text()).items()
            }
        else:
            self.coords = {}

    def save(self) -> None:
        data = {k: list(v) for k, v in self.coords.items()}
        self.path.write_text(json.dumps(data))

    def load(self, name: str) -> Optional[Tuple[int, int, int, int]]:
        return self.coords.get(name)

    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively record a region and store it under *name*."""
        input("Move to top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move to bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        self.coords[name] = region
        self.save()
        return region


def select_region(name: str = "quiz", path: Path | str = "coords.json") -> Tuple[int, int, int, int]:
    """Load a stored region by *name* or interactively create it."""
    selector = RegionSelector(path)
    region = selector.load(name)
    if region is None:
        region = selector.select(name)
    return region
