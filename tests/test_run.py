from unittest.mock import MagicMock, patch

import pytest

import run
from quiz_automation.types import Point, Region


@pytest.mark.parametrize("backend, client_attr", [
    ("chatgpt", "ChatGPTClient"),
    ("local", "LocalModelClient"),
])
def test_main_invokes_runner_with_client_and_stops(backend: str, client_attr: str) -> None:
    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    mock_stats = MagicMock()
    mock_stats.questions_answered = 5

    with patch("run.Settings", return_value=cfg), \
        patch("run.Stats", return_value=mock_stats), \
        patch(f"run.{client_attr}") as mock_client_cls, \
        patch("run.QuizRunner") as mock_runner:

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        runner_instance = MagicMock()
        runner_instance.is_alive.side_effect = [True, False]
        mock_runner.return_value = runner_instance

        run.main([
            "--mode",
            "headless",
            "--backend",
            backend,
            "--max-questions",
            "5",
        ])

        mock_client_cls.assert_called_once_with()
        mock_runner.assert_called_once_with(
            cfg.quiz_region,
            cfg.chat_box,
            cfg.response_region,
            list("ABCD"),
            cfg.option_base,
            model_client=mock_client,
            stats=mock_stats,
        )
        runner_instance.start.assert_called_once()
        runner_instance.stop.assert_called_once()
