import logging
from unittest.mock import MagicMock

import run
from quiz_automation.types import Point, Region


def test_headless_stops_after_max_questions(monkeypatch):
    """Ensure the runner stops once the max question count is reached."""

    class DummyStats:
        def __init__(self) -> None:
            self.questions_answered = 0

    stats = DummyStats()
    monkeypatch.setattr(run, "Stats", MagicMock(return_value=stats))

    class DummyRunner:
        def __init__(self) -> None:
            self.start = MagicMock()
            self.join = MagicMock(side_effect=self._join)
            self.stop = MagicMock(side_effect=self._stop)
            self._alive = True

        def _join(self, timeout: float | None = None) -> None:
            stats.questions_answered = 1

        def _stop(self) -> None:
            self._alive = False

        def is_alive(self) -> bool:
            return self._alive

    runner_instance = DummyRunner()
    mock_runner = MagicMock(return_value=runner_instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    mock_settings = MagicMock(return_value=cfg)
    monkeypatch.setattr(run, "Settings", mock_settings)
    monkeypatch.setattr(run, "configure_logger", MagicMock())

    run.main(["--mode", "headless", "--max-questions", "1"])

    mock_runner.assert_called_once()
    _, kwargs = mock_runner.call_args
    assert kwargs["stats"] is stats
    assert runner_instance.stop.called


def test_config_and_log_level_flags(monkeypatch, tmp_path):
    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    mock_settings = MagicMock(return_value=cfg)
    monkeypatch.setattr(run, "Settings", mock_settings)

    instance = MagicMock()
    instance.is_alive.return_value = False
    monkeypatch.setattr(run, "QuizRunner", MagicMock(return_value=instance))

    mock_configure = MagicMock()
    monkeypatch.setattr(run, "configure_logger", mock_configure)

    config_file = tmp_path / "test.env"
    config_file.write_text("POLL_INTERVAL=2")

    run.main([
        "--mode",
        "headless",
        "--log-level",
        "DEBUG",
        "--config",
        str(config_file),
    ])

    mock_configure.assert_called_once()
    assert mock_configure.call_args.kwargs["level"] == logging.DEBUG
    mock_settings.assert_called_once_with(_env_file=str(config_file))

