from unittest.mock import MagicMock

from quiz_automation.runner import QuizRunner
from quiz_automation import automation
from quiz_automation.types import Point, Region


def test_runner_uses_model_client(monkeypatch):
    calls = {"screenshot": 0, "click": 0, "ask": 0}

    def fake_screenshot(region=None):
        calls["screenshot"] += 1
        return "img"

    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "Q?")

    def fake_click(base, idx, offset=40):
        calls["click"] += 1

    monkeypatch.setattr(automation, "click_option", fake_click)

    model = MagicMock()

    def fake_ask(question, options):
        calls["ask"] += 1
        runner.stop()
        return "A"

    model.ask.side_effect = fake_ask

    runner = QuizRunner(
        Region(0, 0, 10, 10),
        Point(0, 0),
        Region(0, 0, 10, 10),
        ["A", "B"],
        Point(0, 0),
        model=model,
    )

    runner.start()
    runner.join(timeout=1)

    assert calls == {"screenshot": 1, "click": 1, "ask": 1}
    model.ask.assert_called_once_with("Q?", ["A", "B"])
