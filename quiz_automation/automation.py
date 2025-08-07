"""High-level workflow helpers for quiz automation."""
from __future__ import annotations

import importlib
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Sequence, Tuple

from .clicker import click_option
from .model_client import LocalModelClient
from .logger import Logger
from .stats import Stats
from .utils import copy_image_to_clipboard, validate_region, hash_text


def _pyautogui():
    try:  # pragma: no cover
        return importlib.import_module("pyautogui")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pyautogui is required") from exc


def _pytesseract():
    try:  # pragma: no cover
        return importlib.import_module("pytesseract")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pytesseract is required") from exc


def screenshot_region(region: Tuple[int, int, int, int]) -> Any:
    """Capture *region* using pyautogui and return an image object."""
    pg = _pyautogui()
    left, top, _width, _height = region
    pg.moveTo(left, top)
    return pg.screenshot(region=region)


# ---------------------------------------------------------------------------
# Local-model workflow

def answer_question(
    quiz_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    model: LocalModelClient,
    offset: int = 40,
    stats: Optional[Stats] = None,
    logger: Optional[Logger] = None,
) -> str:
    """OCR the quiz region, ask *model*, and click the chosen option."""
    validate_region(quiz_region)
    start_total = time.time()
    img = screenshot_region(quiz_region)

    pt = _pytesseract()
    start = time.time()
    text = pt.image_to_string(img)
    if stats:
        stats.record_ocr(time.time() - start)

    cached = stats.cache_lookup(text) if stats else None
    if cached:
        letter = cached
    else:
        start = time.time()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(model.ask, text, list(options))
            letter = future.result()
        if stats:
            stats.record_model(time.time() - start)
            stats.cache_store(text, letter)

    idx = ord(letter.upper()) - ord("A")
    click_option(option_base, idx, offset)
    if stats:
        stats.record_question(time.time() - start_total)
    if logger:
        logger.log("question", text=text)
        logger.log("answer", letter=letter, index=idx)
    return letter


# ---------------------------------------------------------------------------
def send_to_chatgpt(img: Any, box: Tuple[int, int]) -> None:
    """Focus ChatGPT input, paste *img*, and submit."""
    pg = _pyautogui()
    pg.click(*box)
    copy_image_to_clipboard(img)
    pg.hotkey("ctrl", "v")
    pg.press("enter")


def read_chatgpt_response(
    region: Tuple[int, int, int, int],
    *,
    timeout: float = 20.0,
    poll: float = 1.0,
) -> str:
    """OCR the ChatGPT answer area, refreshing on timeout."""
    pg = _pyautogui()
    pt = _pytesseract()
    start = time.time()
    while time.time() - start < timeout:
        img = pg.screenshot(region=region)
        text = pt.image_to_string(img).strip()
        if text:
            return text
        time.sleep(poll)
    pg.hotkey("ctrl", "r")
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
    logger: Optional[Logger] = None,
) -> str:
    """Send screenshot to ChatGPT UI and click the returned answer."""
    validate_region(quiz_region)
    validate_region(response_region)
    start_total = time.time()
    img = screenshot_region(quiz_region)

    img_hash = None
    if stats:
        img_hash = hash_text(img.tobytes().hex())
        cached = stats.cache.get(img_hash)
    else:
        cached = None

    reply = ""
    if cached:
        letter = cached
    else:
        letter = ""
        for attempt in range(2):
            send_to_chatgpt(img, chatgpt_box)
            reply = read_chatgpt_response(response_region, timeout=timeout)
            letter = _extract_letter(reply)
            if letter:
                break
        if not letter:
            if stats:
                stats.record_error()
            raise ValueError("No valid answer letter detected")
        if stats:
            stats.cache[img_hash] = letter
            stats.record_tokens(len(reply))

    idx = ord(letter) - ord("A")
    click_option(option_base, idx, offset)
    duration = time.time() - start_total
    if stats:
        stats.record_question(duration)
    if logger:
        logger.log("question", image_hash=img_hash)
        logger.log("answer", letter=letter, index=idx, tokens=len(reply), duration=duration)
    return letter
