"""High level helpers orchestrating the quiz answering flow."""
from __future__ import annotations

import logging
import re
import time
from typing import Sequence, Tuple

try:  # pragma: no cover - optional GUI dependencies
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(
        click=lambda *a, **k: None,
        hotkey=lambda *a, **k: None,
        press=lambda *a, **k: None,
        screenshot=lambda *a, **k: None,
        moveTo=lambda *a, **k: None,
    )

try:  # pragma: no cover
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pytesseract = SimpleNamespace(image_to_string=lambda img: "")

from .config import settings
from .utils import copy_image_to_clipboard

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low level helpers


def click_option(base: Tuple[int, int], index: int, offset: int | None = None) -> None:
    """Click the answer option at ``base`` plus ``index`` * offset."""

    y_offset = (offset or settings.click_offset) * index
    x, y = base
    try:
        pyautogui.click(x, y + y_offset)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("click failed: %s", exc)
        raise


def send_to_chatgpt(image, box: Tuple[int, int]) -> None:
    """Paste ``image`` into the ChatGPT text box located at ``box``."""

    try:
        copy_image_to_clipboard(image)
        pyautogui.click(*box)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
    except Exception as exc:  # pragma: no cover
        logger.debug("send_to_chatgpt failed: %s", exc)
        raise


def read_chatgpt_response(region: Tuple[int, int, int, int], timeout: float | None = None) -> str:
    """Poll ``region`` until OCR returns text or ``timeout`` expires."""

    end = time.time() + (timeout or settings.read_timeout)
    while time.time() < end:
        try:
            img = pyautogui.screenshot(region=region)
            text = pytesseract.image_to_string(img).strip()
        except Exception as exc:  # pragma: no cover
            logger.debug("read_chatgpt_response failed: %s", exc)
            text = ""
        if text:
            return text
        time.sleep(0.5)
    raise TimeoutError("no response")


# ---------------------------------------------------------------------------
# High level flow


def _parse_answer(text: str, options: Sequence[str]) -> Tuple[str, int]:
    """Extract the option letter from *text* and return it and its index."""

    match = re.search(r"([A-Z])", text.upper())
    if not match:
        raise ValueError("no option letter found")
    letter = match.group(1)
    return letter, options.index(letter)


def answer_question_via_chatgpt(
    question_region: Tuple[int, int, int, int],
    chatgpt_box: Tuple[int, int],
    response_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    *,
    retries: int = 3,
) -> str:
    """Capture the question, send it to ChatGPT and click the returned option."""

    image = pyautogui.screenshot(region=question_region)
    question = pytesseract.image_to_string(image)
    send_to_chatgpt(question, chatgpt_box)

    for attempt in range(retries):
        try:
            text = read_chatgpt_response(response_region)
            letter, idx = _parse_answer(text, options)
            click_option(option_base, idx)
            return letter
        except TimeoutError:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

    # Should never reach here
    raise TimeoutError("no response")
