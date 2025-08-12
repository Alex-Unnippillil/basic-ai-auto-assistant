from quiz_automation.config import Settings


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

