from __future__ import annotations

"""Event logger that also keeps detailed statistics."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .stats import Stats


@dataclass
class Logger:
    """Persist events and accumulate statistics.

    Events are stored as JSON lines in the optional ``path`` and mirrored in the
    in-memory ``events`` list for easy inspection during testing.
    """

    path: Optional[Path] = None
    stats: Stats = field(default_factory=Stats)
    events: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------------------
    def log_event(self, event: str, **data: Any) -> None:
        record: Dict[str, Any] = {"time": time.time(), "event": event, **data}
        self.events.append(record)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")

    # ------------------------------------------------------------------
    def record_question(self, tokens: int = 0) -> None:
        self.stats.record_question(tokens)
        self.log_event(
            "question",
            tokens=tokens,
            index=self.stats.questions,
            timestamp=self.stats.question_timestamps[-1],
        )

    def record_error(self, message: str = "") -> None:
        self.stats.record_error()
        self.log_event("error", message=message)
