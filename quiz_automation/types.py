"""Basic geometric types used throughout the project."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Point:
    """2D point represented by integer ``x`` and ``y`` coordinates."""

    x: int
    y: int

    def __iter__(self) -> Iterator[int]:  # pragma: no cover - trivial
        """Iterate over the point coordinates."""
        yield self.x
        yield self.y


@dataclass(frozen=True)
class Region:
    """Screen region with ``left``/``top`` coordinates and size."""

    left: int
    top: int
    width: int
    height: int

    def __iter__(self) -> Iterator[int]:  # pragma: no cover - trivial
        """Iterate over the region attributes."""
        yield self.left
        yield self.top
        yield self.width
        yield self.height

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return ``(left, top, width, height)`` tuple."""
        return self.left, self.top, self.width, self.height
