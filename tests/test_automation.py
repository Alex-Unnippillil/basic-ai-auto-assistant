"""Tests for :mod:`quiz_automation.automation`."""

from quiz_automation import automation


def run_answer(monkeypatch, response: str) -> tuple[str, int]:
    """Helper to invoke :func:`automation.answer_question_via_chatgpt`.

    The heavy interactions with the desktop are monkeypatched to simple
    stand‑ins so the logic around parsing the model's answer can be tested.
    Returns the letter chosen by the function and the index passed to
    ``click_option``.
    """

    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation, "read_chatgpt_response", lambda region, timeout=20.0: response
    )

    clicked: dict[str, int] = {}

    def fake_click(base, idx, offset=40):
        clicked["idx"] = idx

    monkeypatch.setattr(automation, "click_option", fake_click)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 0, 0), ["A", "B", "C", "D"], (0, 0)
    )
    return letter, clicked["idx"]


def test_answer_captured_from_simple_format(monkeypatch) -> None:
    letter, idx = run_answer(monkeypatch, "Answer: C")
    assert letter == "C"
    assert idx == 2


def test_answer_with_parentheses(monkeypatch) -> None:
    letter, idx = run_answer(monkeypatch, "The answer is (B)")
    assert letter == "B"
    assert idx == 1


def test_unexpected_response_defaults_to_a(monkeypatch) -> None:
    letter, idx = run_answer(monkeypatch, "something else")
    assert letter == "A"
    assert idx == 0

