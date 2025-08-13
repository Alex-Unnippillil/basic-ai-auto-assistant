import logging
from unittest.mock import MagicMock

import run
from quiz_automation.types import Point, Region


def test_headless_invokes_quiz_runner(monkeypatch):
    instance = MagicMock()
    instance.is_alive.return_value = False
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    monkeypatch.setattr(run, "Settings", MagicMock(return_value=cfg))

    mock_configure = MagicMock()
    monkeypatch.setattr(run, "configure_logger", mock_configure)

    mock_chatgpt = MagicMock(return_value="client")
    mock_local = MagicMock()
    monkeypatch.setattr(run, "ChatGPTClient", mock_chatgpt)
    monkeypatch.setattr(run, "LocalModelClient", mock_local)

    run.main(["--mode", "headless"])

    mock_chatgpt.assert_called_once_with()
    mock_local.assert_not_called()

    args, kwargs = mock_runner.call_args
    assert args == (
        cfg.quiz_region,
        cfg.chat_box,
        cfg.response_region,
        list("ABCD"),
        cfg.option_base,
    )
    assert kwargs["model_client"] == "client"
    assert "stats" in kwargs

    instance.start.assert_called_once_with()
    instance.join.assert_called()


def test_config_and_log_level_flags(monkeypatch, tmp_path):
    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    monkeypatch.setattr(run, "Settings", MagicMock(return_value=cfg))

    instance = MagicMock()
    instance.is_alive.return_value = False
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    mock_configure = MagicMock()
    monkeypatch.setattr(run, "configure_logger", mock_configure)
    mock_chatgpt = MagicMock(return_value="client")
    monkeypatch.setattr(run, "ChatGPTClient", mock_chatgpt)
    mock_local = MagicMock(return_value="local")
    monkeypatch.setattr(run, "LocalModelClient", mock_local)

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
    mock_chatgpt.assert_not_called()
    mock_local.assert_called_once_with()
    mock_runner.assert_called_once()
    assert mock_runner.call_args.kwargs["model_client"] == "local"
    assert mock_runner.call_args.args[0] == cfg.quiz_region
