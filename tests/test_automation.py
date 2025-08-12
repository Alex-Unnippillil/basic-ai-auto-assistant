

"""Tests for :mod:`quiz_automation.automation`."""

from quiz_automation import automation


def test_extracts_letter_and_clicks_correct_index(monkeypatch):
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation,
        "read_chatgpt_response",
        lambda region, timeout=20.0: "The answer is c)",
    )

    captured = {}

    def fake_click(base, idx, offset=40):
        captured["idx"] = idx

    monkeypatch.setattr(automation, "click_option", fake_click)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 10, 10), ["A", "B", "C", "D"], (0, 0)
    )

    assert letter == "C"
    assert captured["idx"] == 2


def test_falls_back_to_alphabetical_index(monkeypatch):
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation,
        "read_chatgpt_response",
        lambda region, timeout=20.0: "Answer D",
    )

    captured = {}

    def fake_click(base, idx, offset=40):
        captured["idx"] = idx

    monkeypatch.setattr(automation, "click_option", fake_click)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 10, 10), ["A", "B", "C"], (0, 0)
    )

    assert letter == "D"
    assert captured["idx"] == 3

