from __future__ import annotations

"""Light‑weight computer vision helpers used in tests.

The real project uses more advanced OpenCV based logic.  For the unit tests we
only need a very small subset which is implemented here.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

try:  # pragma: no cover - OpenCV is optional
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore


@dataclass
class UIElement:
    """Representation of a detected UI element."""

    name: str
    box: Tuple[int, int, int, int]
    confidence: float


class AdvancedUIDetector:
    """Naive template based detector used for demonstration purposes."""

    def __init__(self, template_path: Optional[str] = None) -> None:
        self.template = None
        if template_path and cv2 is not None:
            try:
                self.template = cv2.imread(template_path, 0)
            except Exception:  # pragma: no cover - file not found
                self.template = None

    def detect_elements(self, frame: Optional[np.ndarray]) -> List[UIElement]:
        if self.template is None or cv2 is None or frame is None:
            return []
        res = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(res)
        h, w = self.template.shape[:2]
        box = (*max_loc, w, h)
        return [UIElement("template", box, float(max_val))]


class LayoutAnalyzer:
    """Small helper that scores a layout of :class:`UIElement` objects."""

    @staticmethod
    def score_layout(elements: List[UIElement]) -> float:
        if not elements:
            return 0.0
        return sum(e.confidence for e in elements) / len(elements)
