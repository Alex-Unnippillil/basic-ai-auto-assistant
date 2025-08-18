"""Runtime statistics for quiz automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock



@dataclass
class Stats:
    """Container tracking per-question metrics.

    The object internally protects its mutable state with a :class:`~threading.Lock`
    so that worker threads can safely update statistics concurrently. Consumers
    such as the GUI read the aggregated properties like
    :attr:`questions_answered` or :attr:`average_time` to display live metrics.
    """

    total_time: float = 0.0
    total_tokens: int = 0
    questions_answered: int = 0
    errors: int = 0
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def record(self, duration: float, tokens: int) -> None:
        """Record timing and token usage for a successful question."""
        with self._lock:
            self.questions_answered += 1
            self.total_time += duration
            self.total_tokens += tokens


    def record_error(self) -> None:
        """Increment the error counter."""
        with self._lock:
            self.errors += 1

    @property
    def average_time(self) -> float:
        """Return the average time taken per question."""
        with self._lock:
            if self.questions_answered == 0:
                return 0.0
            return self.total_time / self.questions_answered

    @property
    def average_tokens(self) -> float:
        """Return the average tokens used per question."""
        with self._lock:
            if self.questions_answered == 0:
                return 0.0
            return self.total_tokens / self.questions_answered
