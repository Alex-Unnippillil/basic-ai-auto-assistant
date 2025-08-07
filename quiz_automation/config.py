"""Configuration module for quiz automation.

Loads environment variables using Pydantic settings. Use python-dotenv
so local development can specify variables in a .env file.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or .env."""

    poll_interval: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
