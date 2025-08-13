from unittest.mock import MagicMock
import logging

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
    mock_settings = MagicMock(return_value=cfg)
    monkeypatch.setattr(run, "Settings", mock_settings)

    mock_configure = MagicMock()
    monkeypatch.setattr(run, "configure_logger", mock_configure)

    mock_client = MagicMock()
    monkeypatch.setattr(run, "ChatGPTClient", MagicMock(return_value=mock_client))
    monkeypatch.setattr(run, "LocalModelClient", MagicMock())

    run.main(["--mode", "headless"])

    mock_settings.assert_called_once_with()
    mock_configure.assert_called_once()
    assert mock_configure.call_args.kwargs["level"] == logging.INFO
    mock_runner.assert_called_once_with(
        cfg.quiz_region,
        cfg.chat_box,
        cfg.response_region,
        list("ABCD"),
        cfg.option_base,
        model=mock_client,
    )
    instance.start.assert_called_once_with()


def test_config_and_log_level_flags(monkeypatch, tmp_path):
    cfg = MagicMock(
        quiz_region=(1, 2, 3, 4),
        chat_box=(5, 6),
        response_region=(7, 8, 9, 10),
        option_base=(11, 12),
    )
    mock_settings = MagicMock(return_value=cfg)
    monkeypatch.setattr(run, "Settings", mock_settings)

    mock_runner = MagicMock()
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    mock_configure = MagicMock()
    monkeypatch.setattr(run, "configure_logger", mock_configure)

    mock_client = MagicMock()
    monkeypatch.setattr(run, "ChatGPTClient", MagicMock(return_value=mock_client))
    monkeypatch.setattr(run, "LocalModelClient", MagicMock())

    config_file = tmp_path / "test.env"
    config_file.write_text("POLL_INTERVAL=2")

    run.main([
        "--mode",
        "headless",
        "--log-level",
        "DEBUG",
        "--config",
        str(config_file),
        "--backend",
        "local",
    ])

    mock_configure.assert_called_once()
    assert mock_configure.call_args.kwargs["level"] == logging.DEBUG
    mock_settings.assert_called_once_with(_env_file=str(config_file))
    mock_runner.assert_called_once()
    run.LocalModelClient.assert_called_once()
    run.ChatGPTClient.assert_not_called()
