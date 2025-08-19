from types import SimpleNamespace
import sys
import pytest

# Provide minimal stubs for optional dependencies so tests run in isolation
sys.modules.setdefault(
    "pydantic",
    SimpleNamespace(
        BaseModel=object,
        ValidationError=Exception,
        field_validator=lambda *a, **k: (lambda f: f),
    ),
)
sys.modules.setdefault(
    "pydantic_settings", SimpleNamespace(BaseSettings=object, SettingsConfigDict=dict)
)
pytest.importorskip("pydantic_settings")

from quiz_automation.runner import QuizRunner
from quiz_automation import automation
from quiz_automation.types import Point, Region


def test_runner_triggers_full_flow(monkeypatch):
    calls = {"screenshot": 0, "paste": 0, "read": 0, "click": 0}

    def fake_screenshot(*, region=None):
        calls["screenshot"] += 1
        return "img"

    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pyautogui, "moveTo", lambda x, y: None)
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "A")

    def fake_send(img, box):
        calls["paste"] += 1

    monkeypatch.setattr(automation, "send_to_chatgpt", fake_send)

    def fake_read(region, timeout=20.0, poll_interval=0.5):
        calls["read"] += 1
        return "Answer A"

    monkeypatch.setattr(automation, "read_chatgpt_response", fake_read)

    def fake_click(base, idx, offset=40):
        calls["click"] += 1

    monkeypatch.setattr(automation, "click_option", fake_click)

    runner = QuizRunner(
        Region(0, 0, 10, 10),
        Point(0, 0),
        Region(0, 0, 10, 10),
        ["A", "B"],
        Point(0, 0),
        max_questions=1,
    )

    runner.start()
    runner.join(timeout=1)

    assert calls == {"screenshot": 1, "paste": 1, "read": 1, "click": 1}
    assert runner.stats.questions_answered == 1
