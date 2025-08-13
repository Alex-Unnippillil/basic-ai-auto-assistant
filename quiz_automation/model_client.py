"""Local heuristic model for choosing quiz answers."""
from __future__ import annotations

import re
from collections import Counter
from typing import Sequence

from .model_protocol import ModelClientProtocol


class LocalModelClient(ModelClientProtocol):
    """Pick the option sharing the most words with the question."""

    def ask(self, question: str, options: Sequence[str]) -> str:
        question_words = Counter(re.findall(r"\w+", question.lower()))
        scores: list[int] = []
        for opt in options:
            opt_words = Counter(re.findall(r"\w+", opt.lower()))
            scores.append(sum((question_words & opt_words).values()))
        idx = max(range(len(options)), key=scores.__getitem__) if options else 0
        return chr(ord("A") + idx)
