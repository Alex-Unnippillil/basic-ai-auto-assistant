"""Utility for interactively selecting screen regions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

try:  # pragma: no cover - optional dependency
    import pyautogui
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod
        def position() -> Tuple[int, int]:
            return (0, 0)


class RegionSelector:
    """Persist and recall user-selected screen regions."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        if self.path.exists():
            loaded = json.loads(self.path.read_text())
            self.regions: Dict[str, Tuple[int, int, int, int]] = {
                k: tuple(v) for k, v in loaded.items()
            }
        else:
            self.regions = {}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.regions))

    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively select a region and store it under *name*."""
        input("Move to top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move to bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        self.regions[name] = region
        self._save()
        return region

    def load(self, name: str) -> Tuple[int, int, int, int] | None:
        """Load a previously saved region."""
        region = self.regions.get(name)
        return tuple(region) if region is not None else None

