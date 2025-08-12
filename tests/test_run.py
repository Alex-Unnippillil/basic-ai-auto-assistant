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


def test_headless_handles_keyboard_interrupt(monkeypatch):
    instance = MagicMock()
    instance.join.side_effect = [KeyboardInterrupt, None]
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    run.main(["--mode", "headless"])

    mock_runner.assert_called_once()
    instance.start.assert_called_once_with()
    assert instance.join.call_count == 2
    instance.stop.assert_called_once_with()

