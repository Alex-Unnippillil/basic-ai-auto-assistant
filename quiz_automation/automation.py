"""High-level workflow orchestrating quiz screenshot to ChatGPT answer selection."""
from __future__ import annotations

import time
from typing import Tuple

try:  # pragma: no cover - optional deps
    import pyautogui
    import pyperclip
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
        def hotkey(*args):
            pass
        @staticmethod
        def click(x=None, y=None):
            pass
        @staticmethod
        def press(key):
            pass
    class pyperclip:  # type: ignore
        @staticmethod
        def copy(text):
            pass
    class pytesseract:  # type: ignore
        @staticmethod
        def image_to_string(img):
            return ""

from typing import Any

from .clicker import click_option


def screenshot_region(region: Tuple[int, int, int, int]) -> Any:
    """Capture *region* using pyautogui and return an image object."""
    left, top, width, height = region
    pyautogui.moveTo(left, top)  # move mouse to show activity
    return pyautogui.screenshot(region=region)


def send_question_to_chatgpt(question: str, input_pos: Tuple[int, int]) -> None:
    """Paste *question* into ChatGPT window at *input_pos* and submit."""
    pyperclip.copy(question)
    pyautogui.hotkey("alt", "tab")  # assume toggles to ChatGPT
    pyautogui.click(*input_pos)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def read_chatgpt_response(region: Tuple[int, int, int, int], timeout: int = 20) -> str:
    """Return OCR text of ChatGPT response area within *timeout* seconds."""
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(img)
        if text.strip():
            return text
        time.sleep(1)
    raise TimeoutError("No response from ChatGPT")


def answer_question(
    quiz_region: Tuple[int, int, int, int],
    chat_input: Tuple[int, int],
    chat_response_region: Tuple[int, int, int, int],
    option_base: Tuple[int, int],
    offset: int = 40,
) -> str:
    """Process one quiz question and click the predicted answer.

    Returns the raw response text for logging or debugging.
    """
    # Screenshot quiz question and OCR
    img = screenshot_region(quiz_region)
    question = pytesseract.image_to_string(img)

    # Send text to ChatGPT and wait for reply
    send_question_to_chatgpt(question, chat_input)
    response = read_chatgpt_response(chat_response_region)

    # parse answer letter
    letter = next((c for c in response.upper() if c in "ABCD"), None)
    if letter is None:
        raise ValueError(f"Could not parse answer from response: {response!r}")

    idx = ord(letter) - ord("A")
    pyautogui.hotkey("alt", "tab")  # return to quiz window
    click_option(option_base, idx, offset)
    return response
