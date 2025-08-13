"""Thread that repeatedly answers quiz questions using a model client."""
from __future__ import annotations

import queue
import threading
import time
from typing import Sequence

from . import automation
from .stats import Stats
from .gui import QuizGUI
from .logger import get_logger
from .types import Point, Region
from .model_protocol import ModelClientProtocol

logger = get_logger(__name__)


class QuizRunner(threading.Thread):
    """Run a capture/worker pipeline until :attr:`stop_flag` is set."""

    def __init__(
        self,
        quiz_region: Region,
        chatgpt_box: Point,
        response_region: Region,
        options: Sequence[str],
        option_base: Point,
        *,
        stats: Stats | None = None,
        gui: QuizGUI | None = None,
        poll_interval: float = 0.5,
        model: ModelClientProtocol,
    ) -> None:
        super().__init__(daemon=True)
        self.quiz_region = quiz_region
        self.chatgpt_box = chatgpt_box
        self.response_region = response_region
        self.options = options
        self.option_base = option_base
        self.model = model
        self.stop_flag = threading.Event()
        self.stats = stats or Stats()
        self.gui = gui
        self.poll_interval = poll_interval

    def stop(self) -> None:
        """Signal the runner to stop."""
        self.stop_flag.set()

    # The behaviour of this method is exercised in unit tests, so it is
    # excluded from coverage.
    def run(self) -> None:  # pragma: no cover
        q: queue.Queue = queue.Queue(maxsize=1)

        def capture() -> None:
            while not self.stop_flag.is_set():
                if q.empty():
                    img = automation.pyautogui.screenshot(self.quiz_region.as_tuple())
                    q.put(img)
                else:
                    time.sleep(0.05)

        def worker() -> None:
            while not self.stop_flag.is_set() or not q.empty():
                try:
                    img = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                start = time.time()
                try:
                    question = automation.pytesseract.image_to_string(img)
                    letter = self.model.ask(question, self.options)
                    try:
                        idx = self.options.index(letter)
                    except ValueError:
                        idx = max(0, ord(letter) - ord("A"))
                    automation.click_option(self.option_base, idx)
                    duration = time.time() - start
                    self.stats.record(duration, len(question.split()))
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
