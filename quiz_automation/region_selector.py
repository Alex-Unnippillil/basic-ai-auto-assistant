"""Utilities for selecting and storing the quiz region on screen."""
from __future__ import annotations

from typing import Tuple

# In a real implementation this would provide a GUI to let the user drag a
# rectangle. For now we simply return a placeholder region.

def select_region() -> Tuple[int, int, int, int]:
    """Return a hard-coded region placeholder.

    Returns
    -------
    tuple
        (left, top, width, height) representing the selected region.
    """
    return (0, 0, 100, 100)
