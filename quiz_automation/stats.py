"""Collect basic timing statistics for OCR and model calls."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Stats:
    ocr_times: List[float] = field(default_factory=list)
    model_times: List[float] = field(default_factory=list)
    questions: int = 0

    def record_ocr(self, duration: float) -> None:
        self.ocr_times.append(duration)

    def record_model(self, duration: float) -> None:
        self.model_times.append(duration)

    def inc_questions(self) -> None:
        self.questions += 1

    def summary(self) -> Dict[str, float]:
        def avg(lst: List[float]) -> float:
            return sum(lst) / len(lst) if lst else 0.0

        return {
            "questions": self.questions,
            "ocr_avg": avg(self.ocr_times),
            "model_avg": avg(self.model_times),
        }
