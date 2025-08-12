from quiz_automation.config import Settings


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("POLL_INTERVAL", "2.5")
    cfg = Settings()
    assert cfg.poll_interval == 2.5


def test_config_default_poll_interval():
    cfg = Settings()
    assert cfg.poll_interval == 1.0


def test_config_model_name_and_temperature_env(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "gpt-test")
    monkeypatch.setenv("TEMPERATURE", "0.7")
    cfg = Settings()
    assert cfg.model_name == "gpt-test"
    assert cfg.temperature == 0.7


def test_config_default_model_and_temperature():
    cfg = Settings()
    assert cfg.model_name == "o4-mini-high"
    assert cfg.temperature == 0.0
