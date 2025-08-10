"""Simple helper for tracking quiz performance."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Stats:
    """Track number of questions asked and how many were correct."""

    asked: int = 0
    correct: int = 0

    def record(self, is_correct: bool) -> None:
        self.asked += 1
        if is_correct:
            self.correct += 1

    @property
    def accuracy(self) -> float:
        return self.correct / self.asked if self.asked else 0.0
