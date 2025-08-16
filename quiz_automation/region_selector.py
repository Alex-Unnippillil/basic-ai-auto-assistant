"""Helper for manually selecting and persisting screen regions.

The real project relies on :mod:`pyautogui` to read the mouse position while a
user hovers over different corners of the desired region.  For the purposes of
the tests, ``pyautogui`` is optional and substituted with a minimal stub when it
cannot be imported.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from .types import Region
from .utils import validate_region

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(position=lambda: (0, 0))  # type: ignore[attr-defined]


@dataclass
class RegionSelector:
    """Persist and recall screen regions.

    Parameters
    ----------
    path:
        Location of the JSON file used to store named regions.
    """

    path: Path
    _regions: Dict[str, Region] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Load existing regions from ``path`` if present."""
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    regions: Dict[str, Region] = {}
                    for k, v in data.items():
                        if (
                            isinstance(k, str)
                            and isinstance(v, (list, tuple))
                            and len(v) == 4
                            and all(isinstance(i, int) for i in v)
                        ):
                            regions[k] = Region(*v)
                        else:
                            raise ValueError("invalid region data")
                    self._regions = regions
                else:
                    raise ValueError("invalid region data")
            except (OSError, json.JSONDecodeError, ValueError):
                self._regions = {}

    def select(self, name: str) -> Region:
        """Interactively select a region and persist it under ``name``.

        The user is prompted (via :func:`input`) to move the mouse to the top
        left and then the bottom right corner of the region.  The coordinates are
        measured using :func:`pyautogui.position`.
        """
        input("Move mouse to top left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move mouse to bottom right and press Enter")
        x2, y2 = pyautogui.position()
        region = Region(x1, y1, x2 - x1, y2 - y1)

        try:
            validate_region(region)
        except ValueError as exc:
            raise ValueError(f"Invalid region selected: {exc}") from exc

        self._regions[name] = region
        try:
            with self.path.open("w", encoding="utf8") as fh:
                json.dump({k: list(v) for k, v in self._regions.items()}, fh)
        except OSError:
            pass

        return region

    def load(self, name: str) -> Region:
        """Return the region stored under ``name``.

        Raises
        ------
        KeyError
            If the region ``name`` has not been saved yet.
        """
        return self._regions[name]
