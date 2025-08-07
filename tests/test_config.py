from quiz_automation.config import Settings


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("POLL_INTERVAL", "2.5")
    cfg = Settings()
    assert cfg.poll_interval == 2.5


def test_config_default_poll_interval():
    cfg = Settings()
    assert cfg.poll_interval == 1.0
