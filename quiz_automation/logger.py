
"""Simple logging helpers for the quiz automation package."""

from __future__ import annotations

import logging
import os
from typing import Final


_CONFIGURED: Final[str] = "_quiz_automation_logging_configured"


def setup_logging() -> None:
    """Configure the root logger.

    The log level can be controlled via the ``LOG_LEVEL`` environment
    variable. If the variable is not set or contains an unknown value, the
    level defaults to :data:`logging.INFO`.
    """

    if getattr(logging, _CONFIGURED, False):
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    setattr(logging, _CONFIGURED, True)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with our standard configuration."""

    setup_logging()
    return logging.getLogger(name)
