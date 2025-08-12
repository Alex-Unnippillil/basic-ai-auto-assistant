from quiz_automation.config import Settings
from quiz_automation.types import Region


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("POLL_INTERVAL", "2.5")
    cfg = Settings()
    assert cfg.poll_interval == 2.5


def test_openai_config_overrides(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "foo")
    monkeypatch.setenv("OPENAI_SYSTEM_PROMPT", "prompt")
    cfg = Settings()
    assert cfg.openai_model == "foo"
    assert cfg.openai_system_prompt == "prompt"


def test_config_default_poll_interval():
    cfg = Settings()
    assert cfg.poll_interval == 1.0


def test_screen_region_defaults():
    cfg = Settings()
    assert cfg.quiz_region == Region(100, 100, 600, 400)


def test_screen_region_env(monkeypatch):
    monkeypatch.setenv("QUIZ_REGION", "[10,20,30,40]")
    cfg = Settings()
    assert cfg.quiz_region == Region(10, 20, 30, 40)

