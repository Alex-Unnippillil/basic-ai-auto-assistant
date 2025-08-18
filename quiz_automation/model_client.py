"""Model client protocol and simple local implementation."""

from __future__ import annotations

import re
from collections import Counter
from importlib import import_module
from typing import List, Protocol, runtime_checkable


@runtime_checkable
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


def load_model_client(spec: str) -> ModelClientProtocol:
    """Dynamically load a model client implementation.

    Parameters
    ----------
    spec:
        Import path in the form ``module:Class`` or ``module.Class``.

    Returns
    -------
    ModelClientProtocol
        An instantiated client object.
    """
    if ":" in spec:
        module_name, class_name = spec.split(":", 1)
    else:
        module_name, class_name = spec.rsplit(".", 1)
    module = import_module(module_name)
    cls = getattr(module, class_name)
    instance = cls()
    if not isinstance(instance, ModelClientProtocol):
        raise TypeError(f"{spec!r} does not implement ModelClientProtocol")
    return instance
