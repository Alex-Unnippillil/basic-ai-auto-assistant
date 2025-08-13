"""Protocol for quiz model clients."""
from __future__ import annotations

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class ModelClientProtocol(Protocol):
    """Minimal protocol for quiz model backends."""

    def ask(self, question: str, options: List[str]) -> str:
        """Return the letter corresponding to the chosen option."""
        ...
