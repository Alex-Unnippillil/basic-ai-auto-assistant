from __future__ import annotations

"""Configuration handling for the quiz automation package."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Simple settings loaded from environment variables.

    Only the options required by the tests are implemented.  Additional values
    can be added transparently without affecting the public API.
    """

    # Interval between successive screen polls when watching for new questions
    poll_interval: float = 1.0
    # API key used by :class:`ChatGPTClient`
    openai_api_key: str = field(default_factory=str)

    def __post_init__(self) -> None:
        """Populate fields from environment variables when available."""
        self.poll_interval = float(os.getenv("POLL_INTERVAL", self.poll_interval))
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)


# A module level singleton mirroring pydantic's ``BaseSettings`` behaviour used
# in the original project.  Tests import ``settings`` directly.
settings = Settings()
