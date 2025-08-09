from __future__ import annotations

"""High level helpers that drive the Quiz UI using ChatGPT."""

import re
import time
from typing import Sequence, Tuple

import pyautogui
import pytesseract

from .logger import Logger
from .utils import copy_image_to_clipboard


def send_to_chatgpt(img, box: Tuple[int, int]) -> None:
    """Paste *img* into the ChatGPT text box located at *box*."""
    pyautogui.moveTo(*box)
    copy_image_to_clipboard(img)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def read_chatgpt_response(region: Tuple[int, int, int, int], timeout: float = 20.0) -> str:
    """Return OCR'd text from *region* waiting up to *timeout* seconds."""
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(img).strip()
        if text:
            return text
        time.sleep(0.5)
    raise TimeoutError("No response captured from ChatGPT")


def click_option(base: Tuple[int, int], idx: int, offset: int = 40) -> None:
    """Click the option at *idx* relative to *base* with vertical *offset*."""
    x, y = base
    pyautogui.moveTo(x, y + idx * offset)
    pyautogui.click()


def answer_question_via_chatgpt(
    quiz_region: Tuple[int, int, int, int],
    chatgpt_box: Tuple[int, int],
    response_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    logger: Logger | None = None,
) -> str:
    """Capture a question and use ChatGPT to answer it.

    Any error raised during the process is logged and re-raised to allow the
    caller to react.  When successful, the question statistics are recorded via
    *logger*.
    """

    try:
        img = pyautogui.screenshot(region=quiz_region)
        send_to_chatgpt(img, chatgpt_box)
        resp = read_chatgpt_response(response_region)
        match = re.search(r"[A-Z]", resp.upper())
        letter = match.group(0) if match else "A"
        idx = ord(letter) - ord("A")
        click_option(option_base, idx)
        if logger is not None:
            # crude token estimate based on response length
            tokens = len(resp.split())
            logger.record_question(tokens)
        return letter
    except Exception as exc:
        if logger is not None:
            logger.record_error(str(exc))
        raise
