from __future__ import annotations

"""Collection of runtime statistics for the quiz automation process."""

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class Stats:
    """Holds counters and timestamps for quiz execution."""

    questions: int = 0
    tokens: int = 0
    errors: int = 0
    question_timestamps: List[float] = field(default_factory=list)

    def record_question(self, tokens: int = 0, timestamp: float | None = None) -> None:
        """Record that a question was answered.

        Parameters
        ----------
        tokens:
            Estimated number of tokens consumed answering the question.
        timestamp:
            Optional timestamp; if not provided the current time is used.
        """

        self.questions += 1
        self.tokens += tokens
        self.question_timestamps.append(timestamp if timestamp is not None else time.time())

    def record_error(self) -> None:
        """Increment the error counter."""
        self.errors += 1
