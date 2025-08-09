from __future__ import annotations

"""High level helpers to interact with the ChatGPT quiz interface."""

import time
from typing import Any, Sequence, Tuple

try:  # pragma: no cover - optional heavy dependency
    import pyautogui  # type: ignore
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    pyautogui = SimpleNamespace(
        screenshot=lambda *a, **k: None,
        moveTo=lambda *a, **k: None,
        hotkey=lambda *a, **k: None,
        click=lambda *a, **k: None,
    )  # type: ignore[attr-defined]
    pytesseract = SimpleNamespace(image_to_string=lambda *a, **k: "")  # type: ignore[attr-defined]

from .utils import copy_image_to_clipboard, validate_region
from .stats import Stats


def send_to_chatgpt(img: Any, box: Tuple[int, int]) -> None:
    """Paste *img* into the ChatGPT input box located at *box*."""

    if not hasattr(pyautogui, "moveTo"):  # pragma: no cover - guard for missing dependency
        raise RuntimeError("pyautogui not available")
    copy_image_to_clipboard(img)
    pyautogui.moveTo(*box)
    # ``hotkey`` is easier for tests to monkeypatch than writing characters
    pyautogui.hotkey("ctrl", "v")


def read_chatgpt_response(response_region: Tuple[int, int, int, int], timeout: float = 20.0) -> str:
    """Return OCR'd text from *response_region* until non-empty or timeout."""

    if not hasattr(pyautogui, "screenshot") or not hasattr(pytesseract, "image_to_string"):  # pragma: no cover
        raise RuntimeError("required libraries not available")
    validate_region(response_region)
    start = time.time()
    while time.time() - start < timeout:
        img = pyautogui.screenshot(response_region)
        text = pytesseract.image_to_string(img).strip()
        if text:
            return text
        time.sleep(0.5)
    raise TimeoutError("No response detected")


def click_option(base: Tuple[int, int], index: int, offset: int = 40) -> None:
    """Click the answer option at *index* using *base* as the first option."""

    if not hasattr(pyautogui, "moveTo"):  # pragma: no cover
        raise RuntimeError("pyautogui not available")
    x, y = base
    pyautogui.moveTo(x, y + index * offset)
    pyautogui.click()


def answer_question_via_chatgpt(
    quiz_image: Any,
    chatgpt_box: Tuple[int, int],
    response_region: Tuple[int, int, int, int],
    options: Sequence[str],
    option_base: Tuple[int, int],
    stats: Stats | None = None,
) -> str:
    """Send *quiz_image* to ChatGPT and click the model's chosen answer."""

    start = time.time()
    send_to_chatgpt(quiz_image, chatgpt_box)
    response = read_chatgpt_response(response_region)
    letter = response.strip().split()[-1].upper() if response else "A"
    try:
        idx = options.index(letter)
    except ValueError:
        idx = max(0, ord(letter) - ord("A"))
    click_option(option_base, idx)

    if stats is not None:
        duration = time.time() - start
        tokens = len(response.split()) if response else 0
        stats.record(duration, tokens)

    return letter
