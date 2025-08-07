"""High-level workflow helpers for quiz automation."""
from __future__ import annotations

import time
from typing import Any, Optional, Sequence, Tuple

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

        @staticmethod
        def click(x, y):
            pass

        @staticmethod
        def hotkey(*_keys):
            pass

        @staticmethod
        def press(_key):
            pass

    class pytesseract:  # type: ignore
        @staticmethod
        def image_to_string(img):
            return ""

from .clicker import click_option
from .model_client import LocalModelClient
from .stats import Stats
from .utils import copy_image_to_clipboard


def screenshot_region(region: Tuple[int, int, int, int]) -> Any:
    """Capture *region* using pyautogui and return an image object."""
    left, top, _width, _height = region
    pyautogui.moveTo(left, top)
    return pyautogui.screenshot(region=region)


# ---------------------------------------------------------------------------
# Local-model workflow

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


# ---------------------------------------------------------------------------
def send_to_chatgpt(img: Any, box: Tuple[int, int]) -> None:
    """Focus ChatGPT input, paste *img*, and submit."""
    pyautogui.click(*box)
    copy_image_to_clipboard(img)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def read_chatgpt_response(
    region: Tuple[int, int, int, int],
    *,
    timeout: float = 20.0,
    poll: float = 1.0,
) -> str:
    """OCR the ChatGPT answer area, refreshing on timeout."""
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(img).strip()
        if text:
            return text
        time.sleep(poll)
    pyautogui.hotkey("ctrl", "r")
    return ""


def _extract_letter(text: str) -> str:
    for ch in text.upper():
        if ch in "ABCD":
            return ch
    return ""


def answer_question_via_chatgpt(
    quiz_region: Tuple[int, int, int, int],
    chatgpt_box: Tuple[int, int],
    response_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    *,
    offset: int = 40,
    timeout: float = 20.0,
    stats: Optional[Stats] = None,
) -> str:
    """Send screenshot to ChatGPT UI and click the returned answer."""
    img = screenshot_region(quiz_region)
    send_to_chatgpt(img, chatgpt_box)
    reply = read_chatgpt_response(response_region, timeout=timeout)
    letter = _extract_letter(reply)
    if not letter:
        raise ValueError("No valid answer letter detected")
    idx = ord(letter) - ord("A")
    click_option(option_base, idx, offset)
    if stats:
        stats.inc_questions()
    return letter
