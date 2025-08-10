"""Application configuration and defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Runtime settings loaded from environment variables.

    Environment variables are read at instantiation time so tests can modify
    them via ``monkeypatch``.
    """

    openai_api_key: str = ""
    poll_interval: float = 1.0
    read_timeout: float = 20.0
    click_offset: int = 40

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.poll_interval = float(os.getenv("POLL_INTERVAL", self.poll_interval))
        self.read_timeout = float(os.getenv("READ_TIMEOUT", self.read_timeout))
        self.click_offset = int(os.getenv("CLICK_OFFSET", self.click_offset))


# A module level instance is convenient for small scripts and mirrors how the
# rest of the project expects settings to be accessed.
settings = Settings()
