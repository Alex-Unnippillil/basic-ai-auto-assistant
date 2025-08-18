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
    )
    stats = SimpleNamespace(questions_answered=0)
    instantiated = {}

    class DummyClient:
        def __init__(self, *a, **k):
            instantiated["created"] = True

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
        temperature=0.0,
    )
    stats = SimpleNamespace(questions_answered=0)
    captured = SimpleNamespace(temp=None)

    class DummyClient:
        def __init__(self, *a, **k):
            captured.temp = global_settings.temperature

    with patch.object(run, "Settings", return_value=cfg), patch.object(
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
    global_settings.temperature = 0.0


def test_cli_propagates_model_prompt_and_ocr(monkeypatch) -> None:
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

    original = SimpleNamespace(
        openai_model=global_settings.openai_model,
        openai_system_prompt=global_settings.openai_system_prompt,
        ocr_backend=global_settings.ocr_backend,
        openai_api_key=global_settings.openai_api_key,
    )

    cfg = SimpleNamespace(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
        openai_model="test-model",
        openai_system_prompt="system!",
        ocr_backend="dummy",
        openai_api_key="key",
        temperature=0.0,
    )

    stats = SimpleNamespace(questions_answered=0)
    captured = SimpleNamespace(model=None, prompt=None, ocr=None, key=None)

    class DummyClient:
        def __init__(self, *a, **k):
            captured.model = global_settings.openai_model
            captured.prompt = global_settings.openai_system_prompt
            captured.ocr = global_settings.ocr_backend
            captured.key = global_settings.openai_api_key

    with patch.object(run, "Settings", return_value=cfg), patch.object(
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
                "--max-questions",
                "0",
            ]
        )

    assert captured.model == "test-model"
    assert captured.prompt == "system!"
    assert captured.ocr == "dummy"
    assert captured.key == "key"

    global_settings.openai_model = original.openai_model
    global_settings.openai_system_prompt = original.openai_system_prompt
    global_settings.ocr_backend = original.ocr_backend
    global_settings.openai_api_key = original.openai_api_key
