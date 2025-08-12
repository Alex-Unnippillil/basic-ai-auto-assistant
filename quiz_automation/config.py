from __future__ import annotations

"""Configuration handling for the quiz automation package."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read configuration from environment variables."""

    openai_api_key: str | None = None
    openai_model: str = "o4-mini-high"
    openai_system_prompt: str = "Reply with JSON {'answer':'A|B|C|D'}"
    poll_interval: float = 1.0
    model_name: str = "o4-mini-high"
    temperature: float = 0.0

    quiz_region: tuple[int, int, int, int] = (100, 100, 600, 400)
    chat_box: tuple[int, int] = (800, 900)
    response_region: tuple[int, int, int, int] = (100, 550, 600, 150)
    option_base: tuple[int, int] = (100, 520)

    @field_validator(
        "quiz_region", "chat_box", "response_region", "option_base", mode="before"
    )
    @classmethod
    def _parse_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(int(part.strip()) for part in value.split(","))
        return value

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")


# A module-level settings instance convenient for components that do not need
# their own configuration object.
settings = Settings()
