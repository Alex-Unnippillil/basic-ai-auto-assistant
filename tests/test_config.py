from quiz_automation.config import Settings


def test_config_loads_env(monkeypatch):
    """Environment variables should override defaults."""

    monkeypatch.setenv("POLL_INTERVAL", "2.5")
    monkeypatch.setenv("OPENAI_API_KEY", "token")
    cfg = Settings()
    assert cfg.poll_interval == 2.5
    assert cfg.openai_api_key == "token"


def test_config_defaults(monkeypatch):
    """Unset variables fall back to their default values."""

    monkeypatch.delenv("POLL_INTERVAL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cfg = Settings()
    assert cfg.poll_interval == 1.0
    assert cfg.openai_api_key is None
