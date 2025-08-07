"""High-level workflow orchestrating quiz screenshot to ChatGPT answer selection."""
from __future__ import annotations




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

    response = read_chatgpt_response(chat_response_region)

    # parse answer letter
    letter = next((c for c in response.upper() if c in "ABCD"), None)
    if letter is None:
        raise ValueError(f"Could not parse answer from response: {response!r}")

    idx = ord(letter) - ord("A")
    pyautogui.hotkey("alt", "tab")  # return to quiz window
    click_option(option_base, idx, offset)
    return response
