"""Application settings loaded from environment variables.

The project relies on a couple of configuration values which are best
expressed as environment variables.  This module defines a small wrapper
around :class:`pydantic_settings.BaseSettings` so that settings can be
validated and documented in a central location.  A `.env` file is also
respected which keeps the test-suite hermetic and simple to configure.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values for the automation project.

    Attributes
    ----------
    openai_api_key:
        API key used when communicating with the OpenAI service.  The key is
        optional so unit tests can run without external access.
    poll_interval:
        Number of seconds to wait between polling loops for background threads
        such as the :class:`~quiz_automation.watcher.Watcher`.  The default is
        one second which keeps CPU usage low during tests.
    """

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    poll_interval: float = Field(default=1.0, alias="POLL_INTERVAL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# A module level instance is convenient for modules that just need read-only
# access to configuration.  Tests can still instantiate ``Settings`` directly
# for isolated configuration.
settings = Settings()


__all__ = ["Settings", "settings"]

