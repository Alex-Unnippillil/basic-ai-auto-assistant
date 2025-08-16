"""Computer vision helpers for locating quiz UI elements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

try:  # pragma: no cover - optional heavy dependency
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore


@dataclass
class UIElement:
    """Basic representation of a detected UI element."""

    name: str
    bbox: Tuple[int, int, int, int]
    confidence: float


class AdvancedUIDetector:
    """Locate quiz checkboxes via simple template matching.

    The implementation is intentionally lightweight so unit tests can mock
    OpenCV calls.  A production version would include more robust handling and
    additional heuristics.
    """

    def __init__(self, template_path: str | None = None) -> None:
        """Initialise the detector, optionally loading a template image."""
        self.template_path = template_path
        self.template = None
        if template_path and cv2 is not None:
            try:  # pragma: no cover - file IO
                self.template = cv2.imread(template_path, 0)
            except Exception:
                self.template = None

    def detect_elements(self, frame) -> List[UIElement]:
        """Return a list of detected UI elements.

        A real implementation would perform template matching and contour
        analysis.  Here we simply return an empty list when OpenCV is missing or
        when no template is supplied.
        """
        if cv2 is None or self.template is None:
            return []
        result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        h, w = self.template.shape[:2]
        if max_val > 0.8:
            x, y = max_loc
            return [UIElement("checkbox", (x, y, w, h), float(max_val))]
        return []


class LayoutAnalyzer:
    """Assign a simple confidence score for a set of UI elements."""

    @staticmethod
    def score_layout(elements: List[UIElement]) -> float:
        """Return the average confidence score for *elements*."""
        if not elements:
            return 0.0
        return sum(e.confidence for e in elements) / len(elements)
