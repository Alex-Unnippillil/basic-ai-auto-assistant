"""Tests for the CLI entry point in :mod:`run`.

This suite avoids spawning real threads by patching :class:`QuizRunner` with a
``MagicMock``.  The test exercises both supported ``--backend`` values and
verifies that the runner is stopped once the ``--max-questions`` limit is
reached.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest



@pytest.mark.parametrize("backend, client_attr", [
    ("chatgpt", "ChatGPTClient"),
    ("local", "LocalModelClient"),
])
def test_cli_uses_selected_backend_and_stops(backend: str, client_attr: str) -> None:
    """Simulate CLI invocation and ensure the runner is configured correctly."""

    import importlib, sys

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
    cfg = SimpleNamespace(
        quiz_region=Region(1, 2, 3, 4),
        chat_box=Point(5, 6),
        response_region=Region(7, 8, 9, 10),
        option_base=Point(11, 12),
    )
