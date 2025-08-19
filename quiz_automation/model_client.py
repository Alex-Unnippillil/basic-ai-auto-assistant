"""Model client protocol and simple local implementation."""

from __future__ import annotations

import re
from collections import Counter
from typing import List, Protocol

import requests


class ModelClientProtocol(Protocol):
    """Minimal protocol for quiz model backends."""

    def ask(self, question: str, options: List[str]) -> str:
        """Return the letter corresponding to the chosen option."""


class LocalModelClient:
    """Pick the option sharing the most words with the question."""

    def ask(self, question: str, options: List[str]) -> str:
        """Return the letter of the option most related to the question."""
        question_words = Counter(re.findall(r"\w+", question.lower()))
        scores: List[int] = []
        for opt in options:
            opt_words = Counter(re.findall(r"\w+", opt.lower()))
            scores.append(sum((question_words & opt_words).values()))
        idx = max(range(len(options)), key=scores.__getitem__) if options else 0
        return chr(ord("A") + idx)


class RemoteModelClient:
    """HTTP client that forwards questions to a remote service."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def ask(self, question: str, options: List[str]) -> str:
        """Send the question to the remote model and return the chosen letter."""
        response = requests.post(
            f"{self.base_url}/answer",
            json={"question": question, "options": options},
            timeout=10,
        )
        letter = response.json().get("letter")
        if not isinstance(letter, str) or len(letter) != 1:
            msg = f"Invalid response from remote model: {response.text}"
            raise ValueError(msg)
        return letter
