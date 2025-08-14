import pytest
from unittest.mock import MagicMock

pytest.importorskip("pydantic_settings")

import run
from quiz_automation.types import Point, Region


def test_run_headless(monkeypatch):
    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    monkeypatch.setattr("quiz_automation.config.Settings", lambda *_args, **_kw: cfg)
    runner = MagicMock(start=lambda: None, join=lambda timeout=None: None, is_alive=lambda: False, stop=lambda: None)
    monkeypatch.setattr("quiz_automation.runner.QuizRunner", lambda *a, **k: runner)
    run.main(["--mode", "headless", "--max-questions", "1"])
