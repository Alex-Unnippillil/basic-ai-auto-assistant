"""Core automation helpers for interacting with the ChatGPT UI.

The real project performs a number of GUI operations such as capturing the
question area, pasting it into ChatGPT and then clicking the answer option
returned by the model.  The implementations here intentionally avoid any
real GUI interaction so that the unit tests remain deterministic and do not
require a display.  All heavy lifting is delegated to small helper functions
which are easy to monkeypatch in tests.
"""

from __future__ import annotations

import time
from typing import Sequence, Tuple

try:  # pragma: no cover - optional dependency in tests
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - headless fallback
    class _DummyPyAutoGUI:
        def screenshot(self, region=None):
            raise RuntimeError("pyautogui not available")

        def moveTo(self, x, y):
            pass

        def click(self, x=None, y=None):
            pass

        def hotkey(self, *args, **kwargs):
            pass

    pyautogui = _DummyPyAutoGUI()  # type: ignore

import pytesseract

from .utils import copy_image_to_clipboard, validate_region

Region = Tuple[int, int, int, int]
Point = Tuple[int, int]


def send_to_chatgpt(img, chatgpt_box: Point) -> None:
    """Paste *img* into the ChatGPT input box located at ``chatgpt_box``."""

    copy_image_to_clipboard(img)
    pyautogui.moveTo(*chatgpt_box)
    pyautogui.click()
    # ``hotkey`` allows tests to monkeypatch easily; real implementation would
    # perform an actual paste operation.
    pyautogui.hotkey("ctrl", "v")


def read_chatgpt_response(region: Region, timeout: float = 20.0) -> str:
    """Read text from *region* until non-empty or ``timeout`` expires."""

    validate_region(region)
    end = time.time() + timeout
    while time.time() < end:
        img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(img).strip()
        if text:
            return text
        time.sleep(0.5)
    raise TimeoutError("No response detected from ChatGPT")


def click_option(base: Point, index: int, offset: int = 40) -> None:
    """Click the option at *index* starting from ``base`` with vertical *offset*."""

    x, y = base
    pyautogui.moveTo(x, y + index * offset)
    pyautogui.click()


def answer_question_via_chatgpt(
    quiz_region: Region,
    chatgpt_box: Point,
    response_region: Region,
    options: Sequence[str],
    option_base: Point,
) -> str:
    """Full flow from capturing question to clicking the chosen answer."""

    image = pyautogui.screenshot(region=quiz_region)
    send_to_chatgpt(image, chatgpt_box)
    response = read_chatgpt_response(response_region)
    # Find first letter corresponding to an option
    for idx, _opt in enumerate(options):
        letter = chr(ord("A") + idx)
        if letter in response:
            click_option(option_base, idx)
            return letter
    return ""  # No matching option found


__all__ = [
    "send_to_chatgpt",
    "read_chatgpt_response",
    "click_option",
    "answer_question_via_chatgpt",
]

