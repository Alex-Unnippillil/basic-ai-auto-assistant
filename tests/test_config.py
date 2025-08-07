from quiz_automation.config import Settings


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    cfg = Settings()
    assert cfg.openai_api_key == "test"


def test_config_default_poll_interval(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    cfg = Settings()
    assert cfg.poll_interval == 1.0
