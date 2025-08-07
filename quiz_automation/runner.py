"""Thread that repeatedly answers quiz questions via the ChatGPT UI."""
from __future__ import annotations

import threading
from typing import Sequence, Tuple

from .automation import answer_question_via_chatgpt


class QuizRunner(threading.Thread):
    """Call :func:`answer_question_via_chatgpt` in a loop until stopped."""

    def __init__(
        self,
        quiz_region: Tuple[int, int, int, int],
        chatgpt_box: Tuple[int, int],
        response_region: Tuple[int, int, int, int],
        options: Sequence[str],
        option_base: Tuple[int, int],
    ) -> None:
        super().__init__(daemon=True)
        self.quiz_region = quiz_region
        self.chatgpt_box = chatgpt_box
        self.response_region = response_region
        self.options = options
        self.option_base = option_base
        self.stop_flag = threading.Event()

    def run(self) -> None:  # pragma: no cover - behaviour tested indirectly
        while not self.stop_flag.is_set():
            answer_question_via_chatgpt(
                self.quiz_region,
                self.chatgpt_box,
                self.response_region,
                self.options,
                self.option_base,
            )
