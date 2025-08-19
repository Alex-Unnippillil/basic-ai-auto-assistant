"""Runtime statistics for quiz automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock

from sqlalchemy.orm import Session


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
    db_session: Session | None = None
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def record(self, duration: float, tokens: int) -> None:
        """Record timing and token usage for a successful question."""
        with self._lock:
            self.questions_answered += 1
            self.total_time += duration
            self.total_tokens += tokens

            if self.db_session is not None:
                from .persistence import Question, SessionStat

                self.db_session.add(Question(duration=duration, tokens=tokens))

                stat = self.db_session.get(SessionStat, 1)
                if stat is None:
                    stat = SessionStat(
                        id=1,
                        total_time=self.total_time,
                        total_tokens=self.total_tokens,
                        questions_answered=self.questions_answered,
                        errors=self.errors,
                    )
                    self.db_session.add(stat)
                else:
                    stat.total_time = self.total_time
                    stat.total_tokens = self.total_tokens
                    stat.questions_answered = self.questions_answered
                    stat.errors = self.errors

                self.db_session.commit()

    def record_error(self) -> None:
        """Increment the error counter."""
        with self._lock:
            self.errors += 1

            if self.db_session is not None:
                from .persistence import SessionStat

                stat = self.db_session.get(SessionStat, 1)
                if stat is None:
                    stat = SessionStat(
                        id=1,
                        total_time=self.total_time,
                        total_tokens=self.total_tokens,
                        questions_answered=self.questions_answered,
                        errors=self.errors,
                    )
                    self.db_session.add(stat)
                else:
                    stat.errors = self.errors

                self.db_session.commit()

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
