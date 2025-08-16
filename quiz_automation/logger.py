"""Utility helpers for package logging configuration."""

import inspect
import logging
from typing import Optional

DEFAULT_FORMAT = "%(levelname)s:%(name)s:%(message)s"


def configure_logger(
    level: int = logging.INFO, fmt: str = DEFAULT_FORMAT
) -> logging.Logger:
    """Configure and return the root logger for the package.

    Parameters
    ----------
    level:
        Logging level to be applied to the package logger.
    fmt:
        Formatter string used for the attached :class:`logging.StreamHandler`.
    """
    logger = logging.getLogger("quiz_automation")
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger bound to *name* or the caller's module.

    When *name* is ``None`` the module name of the caller is used.  This mirrors
    the common pattern ``logging.getLogger(__name__)`` while avoiding repetition
    in modules that want a logger associated with their ``__name__``.
    """
    if name is None:
        frame = inspect.stack()[1]
        name = frame.frame.f_globals.get("__name__", "quiz_automation")
    return logging.getLogger(name)


# Configure the package logger with default settings on import so that modules
# can immediately log messages.  Tests or applications can call
# :func:`configure_logger` again to customise behaviour.
configure_logger()
