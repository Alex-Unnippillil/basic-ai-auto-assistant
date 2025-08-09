"""Configuration handling for the quiz automation package."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Configuration loaded from environment variables.

    Attributes
    ----------
    openai_api_key:
        API key used by the OpenAI client. Defaults to the value of the
        ``OPENAI_API_KEY`` environment variable, or ``None`` when the variable
        is unset.
    poll_interval:
        Delay, in seconds, between polling iterations. Defaults to the value
        of ``POLL_INTERVAL`` if set, otherwise ``1.0``.
    """

    openai_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    poll_interval: float = field(
        default_factory=lambda: float(os.getenv("POLL_INTERVAL", "1.0"))
    )


# A module-level settings instance convenient for components that do not need
# their own configuration object.
settings = Settings()
