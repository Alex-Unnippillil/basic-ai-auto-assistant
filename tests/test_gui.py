import sys
from types import SimpleNamespace

import pytest

# Provide lightweight stand-ins for optional dependencies so importing the
# package does not require the real libraries.
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

from quiz_automation.gui import QuizGUI


def test_gui_buttons_trigger_runner_methods():
    gui = QuizGUI()
    calls = []

    class DummyRunner:
        def pause(self):
            calls.append("pause")

        def resume(self):
            calls.append("resume")

        def stop(self):
            calls.append("stop")

    runner = DummyRunner()
    gui.connect_runner(runner)

    # Simulate button presses; fall back to direct emitters when Qt is absent
    if getattr(gui, "_pause_btn", None) is not None:
        gui._pause_btn.click()
        gui._resume_btn.click()
        gui._stop_btn.click()
    else:
        gui._emit_pause()
        gui._emit_resume()
        gui._emit_stop()

    assert calls == ["pause", "resume", "stop"]
