from __future__ import annotations

"""Configuration handling for the quiz automation package."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read configuration from environment variables."""

    openai_api_key: str | None = None
    poll_interval: float = 1.0
    model_name: str = "o4-mini-high"
    temperature: float = 0.0

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")


# A module-level settings instance convenient for components that do not need
# their own configuration object.
settings = Settings()
