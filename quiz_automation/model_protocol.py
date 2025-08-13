from __future__ import annotations

"""Protocol for model clients that answer quiz questions."""

from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class ModelClientProtocol(Protocol):
    """Client capable of answering multiple choice questions."""

    def ask(self, question: str, options: Sequence[str]) -> str:
        """Return the chosen option letter for *question*.

        Implementations should return a single uppercase letter corresponding
        to the index of the selected option (``"A"`` for the first option,
        ``"B"`` for the second, etc.).
        """
        ...
