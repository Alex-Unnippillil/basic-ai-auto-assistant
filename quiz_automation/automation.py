"""Utilities to interact with the ChatGPT UI for multiple choice quizzes.

The real project communicates with a desktop browser using :mod:`pyautogui`
and reads ChatGPT's responses via :mod:`pytesseract`.  Those heavy
dependencies are optional for the tests in this kata, therefore the module
gracefully degrades to no-op stand‑ins when they are missing.  The helpers
exposed here provide a small, well documented surface area used throughout the
project and in the unit tests.
"""

from __future__ import annotations

import re
import time
from typing import Any, Sequence

try:  # pragma: no cover - optional heavy dependency
    import pyautogui  # type: ignore
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    # ``pyautogui`` and ``pytesseract`` are not available in the execution
    # environment.  Provide very small mocks so the rest of the code can still
    # be exercised.  Each attribute mimics the interface used in this module
    # which allows the tests to monkeypatch behaviour if required.
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(  # type: ignore[attr-defined]
        screenshot=lambda *_, **__: None,
        moveTo=lambda *_, **__: None,
        hotkey=lambda *_, **__: None,
        click=lambda *_, **__: None,
    )
    pytesseract = SimpleNamespace(  # type: ignore[attr-defined]
        image_to_string=lambda *_, **__: "",
    )

from . import ocr
from .clicker import Clicker
from .config import settings
from .logger import get_logger
from .model_client import ModelClientProtocol
from .stats import Stats
from .types import Point, Region
from .utils import copy_image_to_clipboard, validate_region

logger = get_logger(__name__)

__all__ = [
    "send_to_chatgpt",
    "read_chatgpt_response",
    "click_option",
    "answer_question",
]


def send_to_chatgpt(img: Any, box: Point) -> None:
    """Paste *img* into the ChatGPT input box located at ``box``.

    Parameters
    ----------
    img:
        Image object to be pasted into the ChatGPT input box.
    box:
        Screen coordinates for the chat input area.

    Raises
    ------
    RuntimeError
        If :mod:`pyautogui` is not available.
    """
    if not hasattr(pyautogui, "moveTo"):
        raise RuntimeError("pyautogui not available")

    if not copy_image_to_clipboard(img):
        raise RuntimeError("failed to copy image to clipboard")
    pyautogui.moveTo(*box)
    # ``hotkey`` is easier for tests to monkeypatch than writing characters
    pyautogui.hotkey("ctrl", "v")


def read_chatgpt_response(
    response_region: Region,
    timeout: float = 20.0,
    poll_interval: float = 0.5,
) -> str:
    """Return OCR'd text from ``response_region`` until non-empty or timeout.

    Parameters
    ----------
    response_region:
        The screen rectangle containing ChatGPT's textual response.
    timeout:
        Maximum number of seconds to wait for a non-empty OCR result.
    poll_interval:
        Seconds to wait between OCR attempts.

    Returns
    -------
    str
        The stripped OCR text.

    Raises
    ------
    RuntimeError
        If the required libraries are unavailable.
    TimeoutError
        If no non-empty text is detected within ``timeout`` seconds.
    """
    if not hasattr(pyautogui, "screenshot") or not hasattr(
        pytesseract, "image_to_string"
    ):
        raise RuntimeError("required libraries not available")

    validate_region(response_region)
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot(response_region.as_tuple())
        text = pytesseract.image_to_string(img).strip()
        if text:
            return text
        time.sleep(poll_interval)

    raise TimeoutError("No response detected")


def click_option(base: Point, index: int, offset: int = 40) -> None:
    """Click the answer option at ``index`` using ``base`` as the first option.

    ``base`` corresponds to the coordinates of the first option on screen.  The
    function increments the ``y`` coordinate by ``offset`` for each subsequent
    option and performs a mouse click at the calculated position via
    :class:`~quiz_automation.clicker.Clicker`.

    Raises
    ------
    RuntimeError
        If :mod:`pyautogui` is not available.
    """
    Clicker(base, offset).click_option(index)


def answer_question(
    quiz_image: Any,
    chatgpt_box: Point,
    response_region: Region,
    options: Sequence[str],
    option_base: Point,
    stats: Stats | None = None,
    poll_interval: float = 0.5,
    client: ModelClientProtocol | None = None,
) -> str:
    """Send ``quiz_image`` to a model and click the chosen answer.

    When ``client`` is ``None`` the image is pasted into the ChatGPT UI and the
    response region is polled until an answer appears.  When ``client`` is
    provided the image is OCR'd using the configured backend and the resulting
    question and option text are forwarded to ``client.ask``.
    """
    start = time.time()
    if client is None:
        send_to_chatgpt(quiz_image, chatgpt_box)
        response = read_chatgpt_response(response_region, poll_interval=poll_interval)
        matches = re.findall(r"[A-D]", response.upper())
        letter = matches[-1] if matches else ""
    else:
        ocr_backend = ocr.get_backend(settings.ocr_backend, lang=settings.ocr_lang)
        text = ocr_backend(quiz_image)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        question_lines: list[str] = []
        option_texts: list[str] = []
        valid_letters = {o.upper() for o in options}
        for line in lines:
            match = re.match(r"([A-Za-z])[).:-]?\s*(.*)", line)
            if match and match.group(1).upper() in valid_letters:
                option_texts.append(match.group(2).strip())
            else:
                question_lines.append(line)
        question_text = " ".join(question_lines)
        response = ""
        letter = client.ask(question_text, option_texts).upper()

    try:
        idx = options.index(letter)
    except ValueError:
        # Fall back to alphabetical ordering; ensures a valid index even if the
        # model returns an unexpected string such as "E".
        letter = letter or "A"
        idx = max(0, min(len(options) - 1, ord(letter) - ord("A")))

    click_option(option_base, idx)
    logger.info("ChatGPT chose %s", letter)

    if stats is not None:
        duration = time.time() - start
        tokens = len(response.split()) if response else 0
        stats.record(duration, tokens)

    return letter
