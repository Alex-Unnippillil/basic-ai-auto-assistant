"""Convenient top-level imports for the quiz_automation package.

This module re-exports the most commonly used classes and helper functions so
that examples can simply import from :mod:`quiz_automation` without needing to
know the internal module layout.  Only a small and well-defined public surface
area is provided here.
"""

from .automation import (
    answer_question,
    click_option,
    read_chatgpt_response,
    send_to_chatgpt,
)
from .gui import QuizGUI
from .runner import QuizRunner
from .stats import Stats

__all__ = [
    "QuizRunner",
    "QuizGUI",
    "answer_question",
    "send_to_chatgpt",
    "read_chatgpt_response",
    "click_option",
    "Stats",
]

