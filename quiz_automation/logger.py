import logging
from datetime import datetime, timezone


class TZFormatter(logging.Formatter):
    """Formatter that uses timezone-aware timestamps."""

    def formatTime(self, record, datefmt=None):  # pragma: no cover - logging internals
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger configured for the project."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(TZFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
