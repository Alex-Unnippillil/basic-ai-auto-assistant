from __future__ import annotations

"""Monitor the screen for new quiz questions and emit events."""

import threading
import time
from queue import Queue
from typing import Tuple

from .config import Settings
from .utils import hash_text
from .logger import get_logger

try:  # pragma: no cover - optional dependency
    from mss import mss
except Exception:  # pragma: no cover
    mss = None  # type: ignore
    get_logger(__name__).warning("mss not available; screen capture disabled")

logger = get_logger(__name__)


def _mss():  # pragma: no cover - tiny wrapper for easier monkeypatching
    if mss is None:
        raise RuntimeError("mss not available")
    return mss


class Watcher(threading.Thread):
    """Background thread that polls the screen for new questions."""

    def __init__(self, region: Tuple[int, int, int, int], queue: Queue, cfg: Settings) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self._last_hash: str | None = None

    # -- basic helpers -------------------------------------------------
    def capture(self):  # pragma: no cover - trivial wrapper
        return _mss().mss().grab(self.region)

    def ocr(self, img) -> str:  # pragma: no cover - placeholder for tests
        return ""

    def is_new_question(self, text: str) -> bool:
        current = hash_text(text)
        if current != self._last_hash:
            self._last_hash = current
            return True
        return False

    # -- thread control ------------------------------------------------
    def stop(self) -> None:
        self.stop_flag.set()

    def pause(self) -> None:
        self.pause_flag.set()

    def resume(self) -> None:
        self.pause_flag.clear()

    # -- main loop -----------------------------------------------------
    def run(self) -> None:  # pragma: no cover - behaviour exercised in tests
        while not self.stop_flag.is_set():
            if self.pause_flag.is_set():
                time.sleep(self.cfg.poll_interval)
                continue
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.queue.put(("question", img, text))
            time.sleep(self.cfg.poll_interval)
