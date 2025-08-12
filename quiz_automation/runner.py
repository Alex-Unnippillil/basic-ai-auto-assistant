"""Thread that repeatedly answers quiz questions via the ChatGPT UI."""
from __future__ import annotations

import queue
import threading
import time
from typing import Sequence, Tuple

from . import automation
from .automation import answer_question_via_chatgpt
from .stats import Stats
from .gui import QuizGUI
from .logger import get_logger

logger = get_logger(__name__)


class QuizRunner(threading.Thread):
    """Run a capture/worker pipeline until :attr:`stop_flag` is set."""

    def __init__(
        self,
        quiz_region: Tuple[int, int, int, int],
        chatgpt_box: Tuple[int, int],
        response_region: Tuple[int, int, int, int],
        options: Sequence[str],
        option_base: Tuple[int, int],
        *,
        stats: Stats | None = None,
        gui: QuizGUI | None = None,
    ) -> None:
        super().__init__(daemon=True)
        self.quiz_region = quiz_region
        self.chatgpt_box = chatgpt_box
        self.response_region = response_region
        self.options = options
        self.option_base = option_base
        self.stop_flag = threading.Event()
        self.stats = stats or Stats()
        self.gui = gui

    def stop(self) -> None:
        """Signal the runner to stop."""
        self.stop_flag.set()

    # The behaviour of this method is tested indirectly via unit tests that
    # patch :func:`answer_question_via_chatgpt`, so it is excluded from coverage
    def run(self) -> None:  # pragma: no cover
        q: queue.Queue = queue.Queue(maxsize=1)

        def capture() -> None:
            while not self.stop_flag.is_set():
                if q.empty():
                    img = automation.pyautogui.screenshot(self.quiz_region)
                    q.put(img)
                else:
                    time.sleep(0.05)

        def worker() -> None:
            while not self.stop_flag.is_set() or not q.empty():
                try:
                    img = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                try:
                    answer_question_via_chatgpt(
                        img,
                        self.chatgpt_box,
                        self.response_region,
                        self.options,
                        self.option_base,
                        stats=self.stats,
                    )
                except Exception:
                    logger.exception("Error while answering question")
                    self.stats.record_error()
                finally:
                    if self.gui is not None:
                        self.gui.update(self.stats)

        t_capture = threading.Thread(target=capture, daemon=True)
        t_worker = threading.Thread(target=worker, daemon=True)
        t_capture.start()
        t_worker.start()
        t_capture.join()
        t_worker.join()
