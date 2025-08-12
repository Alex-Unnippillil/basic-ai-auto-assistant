"""Helper for manually selecting and persisting screen regions.

The real project relies on :mod:`pyautogui` to read the mouse position while a
user hovers over different corners of the desired region.  For the purposes of
the tests, ``pyautogui`` is optional and substituted with a minimal stub when it
cannot be imported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
import json

from .logger import get_logger


log = get_logger(__name__)

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
    _regions: Dict[str, Tuple[int, int, int, int]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf8") as fh:
                    data = json.load(fh)
                    self._regions = {k: tuple(v) for k, v in data.items()}
            except json.JSONDecodeError:
                self._regions = {}
                log.warning(
                    "Malformed region file %s encountered; starting with empty regions",
                    self.path,
                )

    def select(self, name: str) -> Tuple[int, int, int, int]:
        """Interactively select a region and persist it under ``name``.

        The user is prompted (via :func:`input`) to move the mouse to the top
        left and then the bottom right corner of the region.  The coordinates are
        measured using :func:`pyautogui.position`.
        """

        input("Move mouse to top left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move mouse to bottom right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)

        self._regions[name] = region
        with self.path.open("w", encoding="utf8") as fh:
            json.dump(self._regions, fh)

        return region

    def load(self, name: str) -> Tuple[int, int, int, int]:
        """Return the region stored under ``name``.

        Raises
        ------
        KeyError
            If the region ``name`` has not been saved yet.
        """

        return self._regions[name]

    def list_regions(self) -> Dict[str, Tuple[int, int, int, int]]:
        """Return a copy of all stored regions."""

        return dict(self._regions)

