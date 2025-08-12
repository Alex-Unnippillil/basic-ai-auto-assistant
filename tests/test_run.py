from unittest.mock import MagicMock

import run


def test_headless_invokes_quiz_runner(monkeypatch):
    instance = MagicMock()
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    cfg = MagicMock(
        quiz_region=(1, 2, 3, 4),
        chat_box=(5, 6),
        response_region=(7, 8, 9, 10),
        option_base=(11, 12),
    )
    monkeypatch.setattr(run, "Settings", lambda: cfg)

    run.main(["--mode", "headless"])

    mock_runner.assert_called_once_with(
        cfg.quiz_region, cfg.chat_box, cfg.response_region, list("ABCD"), cfg.option_base
    )
    instance.start.assert_called_once_with()

