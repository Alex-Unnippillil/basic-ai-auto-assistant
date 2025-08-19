"""Tests for the CLI entry point in :mod:`run`.

This suite avoids spawning real threads by patching :class:`QuizRunner` with a
``MagicMock``.  The test exercises both supported ``--backend`` values and
verifies that the runner is stopped once the ``--max-questions`` limit is
reached.
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "backend, client_attr",
    [
        ("chatgpt", "ChatGPTClient"),
        ("local", "LocalModelClient"),
    ],
)
def test_cli_uses_selected_backend_and_stops(backend: str, client_attr: str) -> None:
    """Simulate CLI invocation and ensure the runner is configured correctly."""

    import importlib
    import sys

    # Provide lightweight stand-ins for optional dependencies
    sys.modules.setdefault(
        "pydantic",
        SimpleNamespace(
            BaseModel=object,
            ValidationError=Exception,
            field_validator=lambda *a, **k: (lambda f: f),
        ),
    )
    sys.modules.setdefault(
        "pydantic_settings",
        SimpleNamespace(BaseSettings=object, SettingsConfigDict=dict),
    )

    run = importlib.import_module("run")
    from quiz_automation.types import Point, Region

    # Dummy configuration and stats objects returned by patched factories
    _cfg = SimpleNamespace(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
        openai_model="dummy-model",
        openai_system_prompt="dummy-prompt",
        ocr_backend="dummy-ocr",
        temperature=0.0,
    )
    stats = SimpleNamespace(questions_answered=0)
    instantiated = {}

    class DummyClient:
        def __init__(self, *a, **k):
            instantiated["created"] = True

    from quiz_automation.config import settings as global_settings

    with patch.object(run, "Settings", return_value=_cfg), patch.object(
        run, "Stats", return_value=stats
    ), patch.object(run, "QuizRunner") as Runner, patch.object(
        run, client_attr, DummyClient
    ):
        Runner.return_value.is_alive.side_effect = [True, False]
        Runner.return_value.start.return_value = None
        Runner.return_value.join.return_value = None
        Runner.return_value.stop.return_value = None

        run.main([
            "--mode",
            "headless",
            "--backend",
            backend,
            "--max-questions",
            "0",
        ])

    assert instantiated.get("created", False)
    assert Runner.return_value.stop.call_count == 1
    global_settings.openai_model = "o4-mini-high"
    global_settings.openai_system_prompt = "Reply with JSON {'answer':'A|B|C|D'}"
    global_settings.ocr_backend = None
    global_settings.temperature = 0.0
def test_cli_temperature(monkeypatch) -> None:
    import importlib
    import sys

    sys.modules.setdefault(
        "pydantic",
        SimpleNamespace(
            BaseModel=object,
            ValidationError=Exception,
            field_validator=lambda *a, **k: (lambda f: f),
        ),
    )
    sys.modules.setdefault(
        "pydantic_settings",
        SimpleNamespace(BaseSettings=object, SettingsConfigDict=dict),
    )

    run = importlib.import_module("run")
    from quiz_automation.config import settings as global_settings
    from quiz_automation.types import Point, Region

    cfg = SimpleNamespace(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
        openai_model="dummy-model",
        openai_system_prompt="dummy-prompt",
        ocr_backend="dummy-ocr",
        temperature=0.0,
    )
    stats = SimpleNamespace(questions_answered=0)
    captured = SimpleNamespace(temp=None)

    class DummyClient:
        def __init__(self, *a, **k):
            captured.temp = global_settings.temperature

    def fake_settings(**kwargs):
        cfg.temperature = kwargs.get("temperature", cfg.temperature)
        return cfg

    with patch.object(run, "Settings", side_effect=fake_settings), patch.object(
        run, "Stats", return_value=stats
    ), patch.object(run, "QuizRunner") as Runner, patch.object(
        run, "ChatGPTClient", DummyClient
    ):
        Runner.return_value.is_alive.side_effect = [True, False]
        Runner.return_value.start.return_value = None
        Runner.return_value.join.return_value = None
        Runner.return_value.stop.return_value = None

        run.main(
            [
                "--mode",
                "headless",
                "--backend",
                "chatgpt",
                "--temperature",
                "0.7",
                "--max-questions",
                "0",
            ]
        )

    assert captured.temp == 0.7
    assert cfg.temperature == 0.7
    global_settings.openai_model = "o4-mini-high"
    global_settings.openai_system_prompt = "Reply with JSON {'answer':'A|B|C|D'}"
    global_settings.ocr_backend = None
    global_settings.temperature = 0.0


def test_cli_propagates_settings_to_global() -> None:
    import importlib
    import sys

    sys.modules.setdefault(
        "pydantic",
        SimpleNamespace(
            BaseModel=object,
            ValidationError=Exception,
            field_validator=lambda *a, **k: (lambda f: f),
        ),
    )
    sys.modules.setdefault(
        "pydantic_settings",
        SimpleNamespace(BaseSettings=object, SettingsConfigDict=dict),
    )

    run = importlib.import_module("run")
    from quiz_automation.config import settings as global_settings
    from quiz_automation.types import Point, Region

    cfg = SimpleNamespace(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
        openai_model="model-x",
        openai_system_prompt="prompt-y",
        ocr_backend="ocr-z",
        temperature=0.2,
    )
    stats = SimpleNamespace(questions_answered=0)

    class DummyClient:
        def __init__(self, *a, **k):
            pass

    with patch.object(run, "Settings", return_value=cfg), patch.object(
        run, "Stats", return_value=stats
    ), patch.object(run, "QuizRunner") as Runner, patch.object(
        run, "ChatGPTClient", DummyClient
    ):
        Runner.return_value.is_alive.side_effect = [True, False]
        Runner.return_value.start.return_value = None
        Runner.return_value.join.return_value = None
        Runner.return_value.stop.return_value = None

        run.main([
            "--mode",
            "headless",
            "--backend",
            "chatgpt",
            "--max-questions",
            "0",
        ])

    assert global_settings.openai_model == "model-x"
    assert global_settings.openai_system_prompt == "prompt-y"
    assert global_settings.ocr_backend == "ocr-z"
    assert global_settings.temperature == 0.2
    global_settings.openai_model = "o4-mini-high"
    global_settings.openai_system_prompt = "Reply with JSON {'answer':'A|B|C|D'}"
    global_settings.ocr_backend = None
    global_settings.temperature = 0.0
