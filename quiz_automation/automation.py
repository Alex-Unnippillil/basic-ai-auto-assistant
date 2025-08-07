"""High-level workflow orchestrating quiz screenshot to ChatGPT answer selection."""
from __future__ import annotations

import time
from typing import Tuple, Any

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
        def hotkey(*args):
            pass

        @staticmethod
        def click(x=None, y=None):
            pass

        @staticmethod
        def press(key):
            pass

    class pytesseract:  # type: ignore
        @staticmethod
        def image_to_string(img):
            return ""

from .clicker import click_option


def screenshot_region(region: Tuple[int, int, int, int]) -> Any:
    """Capture *region* using pyautogui and return an image object."""
    left, top, width, height = region
    pyautogui.moveTo(left, top)  # move mouse to show activity
    return pyautogui.screenshot(region=region)


def copy_image_to_clipboard(img: Any) -> None:
    """Copy a PIL image to the OS clipboard on Windows.

    The function silently does nothing on platforms where the `win32clipboard`
    module is unavailable, keeping tests portable.
    """
    try:  # pragma: no cover - platform specific
        from io import BytesIO
        import win32clipboard  # type: ignore
        import win32con  # type: ignore

        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except Exception:
        # Non-Windows platforms or clipboard errors are ignored
        pass


def send_image_to_chatgpt(img: Any, input_pos: Tuple[int, int]) -> None:
    """Paste *img* into ChatGPT window at *input_pos* and submit."""
    copy_image_to_clipboard(img)
    try:
        pyautogui.hotkey("alt", "tab")  # assume toggles to ChatGPT
        pyautogui.click(*input_pos)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
    except Exception as exc:  # pragma: no cover - relies on GUI availability
        raise RuntimeError("Failed to send image to ChatGPT") from exc


def read_chatgpt_response(
    region: Tuple[int, int, int, int], timeout: int = 20, retries: int = 1
) -> str:
    """Return OCR text of ChatGPT response area.

    If no text is detected within *timeout* seconds, the page is refreshed with
    ``Ctrl+R`` and the wait is retried up to *retries* times.
    """
    for _ in range(retries + 1):
        start = time.time()
        while time.time() - start < timeout:
            img = pyautogui.screenshot(region=region)
            text = pytesseract.image_to_string(img)
            if text.strip():
                return text
            time.sleep(1)
        try:  # pragma: no cover - GUI hotkey
            pyautogui.hotkey("ctrl", "r")
        except Exception:
            pass
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
    img = screenshot_region(quiz_region)

    # Send image to ChatGPT and wait for reply
    send_image_to_chatgpt(img, chat_input)
    response = read_chatgpt_response(chat_response_region)

    # parse answer letter
    letter = next((c for c in response.upper() if c in "ABCD"), None)
    if letter is None:
        raise ValueError(f"Could not parse answer from response: {response!r}")

    idx = ord(letter) - ord("A")
    pyautogui.hotkey("alt", "tab")  # return to quiz window
    click_option(option_base, idx, offset)
    return response
