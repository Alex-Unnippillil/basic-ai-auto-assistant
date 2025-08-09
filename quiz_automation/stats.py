from __future__ import annotations

"""Runtime statistics for quiz automation."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Stats:
    """Container tracking per-question metrics.

    The object stores lightweight statistics that can be safely updated from
    worker threads without additional locking because all operations mutate
    primitive types or append to lists.  Consumers such as the GUI read the
    aggregated properties like :attr:`questions_answered` or
    :attr:`average_time` to display live metrics.
    """

    question_times: List[float] = field(default_factory=list)
    token_counts: List[int] = field(default_factory=list)
    questions_answered: int = 0
    errors: int = 0

    def record(self, duration: float, tokens: int) -> None:
        """Record timing and token usage for a successful question."""

        self.questions_answered += 1
        self.question_times.append(duration)
        self.token_counts.append(tokens)

    def record_error(self) -> None:
        """Increment the error counter."""

        self.errors += 1

    @property
    def average_time(self) -> float:
        """Return the average time taken per question."""

        if not self.question_times:
            return 0.0
        return sum(self.question_times) / len(self.question_times)

    @property
    def average_tokens(self) -> float:
        """Return the average tokens used per question."""

        if not self.token_counts:
            return 0.0
        return sum(self.token_counts) / len(self.token_counts)
