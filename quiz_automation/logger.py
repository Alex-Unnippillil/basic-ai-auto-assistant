import logging
import os
from .config import settings

LOG_LEVEL = os.getenv("LOG_LEVEL", settings.log_level).upper()

_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)

_root_logger = logging.getLogger("quiz_automation")
if not _root_logger.handlers:
    _root_logger.addHandler(_handler)
_root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the project configuration applied."""
    return _root_logger.getChild(name)
