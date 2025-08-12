from __future__ import annotations

"""Runtime statistics for quiz automation."""

from dataclasses import dataclass, field
from threading import Lock
from typing import List
import threading


@dataclass
class Stats:
    """Container tracking per-question metrics.

    The object internally protects its mutable state with a :class:`~threading.Lock`
    so that worker threads can safely update statistics concurrently. Consumers
    such as the GUI read the aggregated properties like
    :attr:`questions_answered` or :attr:`average_time` to display live metrics.
    """

    question_times: List[float] = field(default_factory=list)
    token_counts: List[int] = field(default_factory=list)
    questions_answered: int = 0
    errors: int = 0
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        self._lock = threading.Lock()

    def record(self, duration: float, tokens: int) -> None:
        """Record timing and token usage for a successful question."""

        with self._lock:
            self.questions_answered += 1
            self.question_times.append(duration)
            self.token_counts.append(tokens)

    def record_error(self) -> None:
        """Increment the error counter."""

        with self._lock:
            self.errors += 1

    @property
    def average_time(self) -> float:
        """Return the average time taken per question."""

        with self._lock:
            if not self.question_times:
                return 0.0
            return sum(self.question_times) / len(self.question_times)

    @property
    def average_tokens(self) -> float:
        """Return the average tokens used per question."""

        with self._lock:
            if not self.token_counts:
                return 0.0
            return sum(self.token_counts) / len(self.token_counts)
