"""Configuration handling for the quiz automation package."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .types import Point, Region


class Settings(BaseSettings):
    """Read configuration from environment variables."""

    openai_api_key: str | None = None
    openai_model: str = "o4-mini-high"
    openai_system_prompt: str = "Reply with JSON {'answer':'A|B|C|D'}"
    poll_interval: float = 1.0
    temperature: float = 0.0
    ocr_backend: str | None = None
    database_url: str | None = None

    quiz_region: Region = Region(100, 100, 600, 400)
    chat_box: Point = Point(800, 900)
    response_region: Region = Region(100, 550, 600, 150)
    option_base: Point = Point(100, 520)

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    @field_validator("poll_interval")
    @classmethod
    def _check_poll_interval(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("poll_interval must be greater than 0")
        return v

    @field_validator("temperature")
    @classmethod
    def _check_temperature(cls, v: float) -> float:
        if v < 0:
            raise ValueError("temperature must be non-negative")
        return v


# A module-level settings instance convenient for components that do not need
# their own configuration object.
settings = Settings()
