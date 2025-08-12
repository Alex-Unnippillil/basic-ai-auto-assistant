from __future__ import annotations

"""Configuration handling for the quiz automation package."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

from .types import Point, Region


class Settings(BaseSettings):
    """Read configuration from environment variables."""

    openai_api_key: str | None = None
    openai_model: str = "o4-mini-high"
    openai_system_prompt: str = "Reply with JSON {'answer':'A|B|C|D'}"
    poll_interval: float = 1.0
    temperature: float = 0.0

    quiz_region: Region = Region(100, 100, 600, 400)
    chat_box: Point = Point(800, 900)
    response_region: Region = Region(100, 550, 600, 150)
    option_base: Point = Point(100, 520)

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")



# A module-level settings instance convenient for components that do not need
# their own configuration object.
settings = Settings()
