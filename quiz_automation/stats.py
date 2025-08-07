"""Collect basic timing statistics for OCR and model calls."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .utils import hash_text


@dataclass
class Stats:
    ocr_times: List[float] = field(default_factory=list)
    model_times: List[float] = field(default_factory=list)
    question_times: List[float] = field(default_factory=list)
    cache: Dict[str, str] = field(default_factory=dict)
    tokens: int = 0
    errors: int = 0
    questions: int = 0

    def record_ocr(self, duration: float) -> None:
        self.ocr_times.append(duration)

    def record_model(self, duration: float) -> None:
        self.model_times.append(duration)

    def record_question(self, duration: float) -> None:
        self.question_times.append(duration)
        self.questions += 1

    def record_tokens(self, count: int) -> None:
        self.tokens += count

    def record_error(self) -> None:
        self.errors += 1

    def cache_lookup(self, text: str) -> Optional[str]:
        return self.cache.get(hash_text(text))

    def cache_store(self, text: str, answer: str) -> None:
        self.cache[hash_text(text)] = answer

    def summary(self) -> Dict[str, float]:
        def avg(lst: List[float]) -> float:
            return sum(lst) / len(lst) if lst else 0.0

        return {
            "questions": self.questions,
            "ocr_avg": avg(self.ocr_times),
            "model_avg": avg(self.model_times),
            "question_avg": avg(self.question_times),
            "tokens": float(self.tokens),
            "errors": float(self.errors),
        }
