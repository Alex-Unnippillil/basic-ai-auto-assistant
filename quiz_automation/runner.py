"""Thread that repeatedly answers quiz questions via the ChatGPT UI."""

from __future__ import annotations

import queue
import threading
import time
from typing import Sequence, TextIO

from . import automation
from .automation import answer_question
from .gui import QuizGUI
from .logger import get_logger
from .model_client import ModelClientProtocol
from .stats import Stats
from .types import Point, Region

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
        model_client: ModelClientProtocol | None = None,
        stats: Stats | None = None,
        gui: QuizGUI | None = None,
        poll_interval: float = 0.5,
        session_log: TextIO | None = None,
    ) -> None:
        """Initialise the runner thread."""
        super().__init__(daemon=True)
        self.quiz_region = quiz_region
        self.chatgpt_box = chatgpt_box
        self.response_region = response_region
        self.options = options
        self.option_base = option_base
        self.model_client = model_client
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self.stats = stats or Stats()
        self.gui = gui
        if self.gui is not None:
            self.gui.connect_runner(self)
        self.poll_interval = poll_interval
        self.session_log = session_log

    def stop(self) -> None:
        """Signal the runner to stop."""
        self.stop_flag.set()

    def pause(self) -> None:
        """Pause processing of new questions."""
        self.pause_flag.set()

    def resume(self) -> None:
        """Resume processing after :meth:`pause`."""
        self.pause_flag.clear()

    # The behaviour of this method is tested indirectly via unit tests that
    # patch :func:`answer_question`, so it is excluded from coverage
    def run(self) -> None:  # pragma: no cover
        """Run the capture and worker threads until stopped."""
        q: queue.Queue = queue.Queue(maxsize=1)

        def capture() -> None:
            while not self.stop_flag.is_set():
                if self.pause_flag.is_set():
                    time.sleep(0.05)
                    continue
                if q.empty():
                    img = automation.pyautogui.screenshot(self.quiz_region.as_tuple())
                    q.put(img)
                else:
                    time.sleep(0.05)

        def worker() -> None:
            while not self.stop_flag.is_set() or not q.empty():
                if self.pause_flag.is_set():
                    time.sleep(0.05)
                    continue
                try:
                    img = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                try:
                    answer_question(
                        img,
                        self.chatgpt_box,
                        self.response_region,
                        self.options,
                        self.option_base,
                        stats=self.stats,
                        poll_interval=self.poll_interval,
                        client=self.model_client,
                        session_log=self.session_log,
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
