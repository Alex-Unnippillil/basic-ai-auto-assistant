from unittest.mock import MagicMock

import run
from quiz_automation.types import Point, Region


def test_headless_invokes_quiz_runner(monkeypatch):
    instance = MagicMock()
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    monkeypatch.setattr(run, "Settings", lambda: cfg)

    run.main(["--mode", "headless"])

    mock_runner.assert_called_once_with(
        cfg.quiz_region, cfg.chat_box, cfg.response_region, list("ABCD"), cfg.option_base
    )
    instance.start.assert_called_once_with()

