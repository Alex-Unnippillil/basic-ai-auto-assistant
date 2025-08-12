from unittest.mock import MagicMock

import run


def test_headless_invokes_quiz_runner(monkeypatch):
    instance = MagicMock()
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    run.main(["--mode", "headless"])

    mock_runner.assert_called_once()
    instance.start.assert_called_once_with()
    instance.join.assert_called_once_with()

