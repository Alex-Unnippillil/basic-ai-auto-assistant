"""High-level workflow using local model and stats."""
from __future__ import annotations

import time
from typing import Any, Sequence, Tuple, Optional

try:  # pragma: no cover - optional deps
    import pyautogui
    import pytesseract
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod
        def screenshot(region=None):
            return None

        @staticmethod
        def moveTo(x, y):
            pass

    class pytesseract:  # type: ignore
        @staticmethod
        def image_to_string(img):
            return ""

from .clicker import click_option
from .model_client import LocalModelClient
from .stats import Stats


def screenshot_region(region: Tuple[int, int, int, int]) -> Any:
    """Capture *region* using pyautogui and return an image object."""
    left, top, width, height = region
    pyautogui.moveTo(left, top)
    return pyautogui.screenshot(region=region)


def answer_question(
    quiz_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    model: LocalModelClient,
    offset: int = 40,
    stats: Optional[Stats] = None,
) -> str:
    """OCR the quiz region, ask *model*, and click the chosen option."""
    img = screenshot_region(quiz_region)

    start = time.time()
    text = pytesseract.image_to_string(img)
    if stats:
        stats.record_ocr(time.time() - start)

    start = time.time()
    letter = model.ask(text, list(options))
    if stats:
        stats.record_model(time.time() - start)
        stats.inc_questions()

    idx = ord(letter.upper()) - ord("A")
    click_option(option_base, idx, offset)
    return letter
