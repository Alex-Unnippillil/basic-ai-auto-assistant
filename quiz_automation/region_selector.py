from __future__ import annotations

"""Utility to capture and persist screen regions."""

from pathlib import Path
import json

try:  # pragma: no cover - best effort for environments without a display
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(position=lambda: (0, 0))  # type: ignore


class RegionSelector:
    """Select rectangular screen regions and persist them to disk."""

    def __init__(self, path: Path):
        self.path = Path(path)
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self._regions = {k: tuple(v) for k, v in raw.items()}
        else:
            self._regions = {}

    def select(self, name: str) -> tuple[int, int, int, int]:
        """Interactively capture a region and store it under ``name``."""

        input("Move cursor to top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move cursor to bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)
        self._regions[name] = region
        self._save()
        return region

    def load(self, name: str) -> tuple[int, int, int, int] | None:
        """Return the stored region named ``name`` if present."""

        region = self._regions.get(name)
        if region is not None:
            return tuple(region)
        return None

    def _save(self) -> None:
        serializable = {k: list(v) for k, v in self._regions.items()}
        self.path.write_text(json.dumps(serializable))

