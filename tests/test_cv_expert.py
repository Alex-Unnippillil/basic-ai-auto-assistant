import types
import numpy as np

from quiz_automation.cv_expert import AdvancedUIDetector, LayoutAnalyzer, UIElement


def test_detector_returns_empty_without_template(monkeypatch):
    detector = AdvancedUIDetector()
    assert detector.detect_elements(None) == []


def test_detector_uses_opencv(monkeypatch):
    fake_cv2 = types.SimpleNamespace(
        imread=lambda path, flag: np.ones((5, 5), dtype=np.uint8),
        matchTemplate=lambda frame, template, method: np.array([[0.9]]),
        minMaxLoc=lambda res: (0.0, 0.9, (0, 0), (5, 5)),
        TM_CCOEFF_NORMED=1,
    )
    monkeypatch.setattr("quiz_automation.cv_expert.cv2", fake_cv2)
    detector = AdvancedUIDetector(template_path="dummy")
    elements = detector.detect_elements(np.zeros((5, 5), dtype=np.uint8))
    assert elements and isinstance(elements[0], UIElement)


def test_layout_analyzer_scores_average():
    elems = [UIElement("a", (0, 0, 1, 1), 0.5), UIElement("b", (0, 0, 1, 1), 1.0)]
    assert LayoutAnalyzer.score_layout(elems) == 0.75
