from unittest.mock import MagicMock


import run
from quiz_automation.types import Point, Region


def _setup_common(monkeypatch):
    cfg = MagicMock(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
    monkeypatch.setattr(run, "Settings", MagicMock(return_value=cfg))
    monkeypatch.setattr(run, "configure_logger", MagicMock())
    return cfg


def test_default_backend_is_chatgpt(monkeypatch):
    _setup_common(monkeypatch)
    instance = MagicMock()
    instance.is_alive.return_value = False
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    mock_chatgpt = MagicMock(return_value="client")
    mock_local = MagicMock()
    monkeypatch.setattr(run, "ChatGPTClient", mock_chatgpt)
    monkeypatch.setattr(run, "LocalModelClient", mock_local)



    mock_chatgpt.assert_called_once_with()
    mock_local.assert_not_called()
    args, kwargs = mock_runner.call_args
    assert kwargs["model_client"] == "client"
    assert kwargs["stats"] is stats_obj
    instance.start.assert_called_once()


def test_local_backend_and_max_questions(monkeypatch):
    _setup_common(monkeypatch)
    instance = MagicMock()
    instance.is_alive.side_effect = [True, False]
    mock_runner = MagicMock(return_value=instance)
    monkeypatch.setattr(run, "QuizRunner", mock_runner)

    mock_chatgpt = MagicMock()
    mock_local = MagicMock(return_value="local")
    monkeypatch.setattr(run, "ChatGPTClient", mock_chatgpt)
    monkeypatch.setattr(run, "LocalModelClient", mock_local)

    stats_obj = MagicMock(questions_answered=2)
    monkeypatch.setattr(run, "Stats", MagicMock(return_value=stats_obj))


