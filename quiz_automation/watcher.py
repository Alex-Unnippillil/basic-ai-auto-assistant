"""Background thread that watches the quiz area for new questions."""

from __future__ import annotations

import threading
import time
from queue import Queue
from typing import Any, Tuple

import pytesseract

from .config import Settings
from .utils import hash_text


Region = Tuple[int, int, int, int]


def _mss() -> Any:  # pragma: no cover - tiny wrapper for easy patching
    """Return the :mod:`mss` module.

    The indirection makes it trivial for unit tests to provide a dummy
    implementation without importing the real heavy dependency.
    """

    import mss

    return mss


class Watcher(threading.Thread):
    """Capture a screen region and emit events when the question changes."""

    def __init__(self, region: Region, queue: Queue, cfg: Settings) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self._pause = threading.Event()
        self._last_hash: str | None = None

    # --- helpers -----------------------------------------------------
    def capture(self):  # pragma: no cover - behaviour mocked in tests
        """Return a screenshot of ``self.region`` using :mod:`mss`."""

        mss = _mss()
        with mss.mss() as sct:
            left, top, width, height = self.region
            bbox = {"left": left, "top": top, "width": width, "height": height}
            return sct.grab(bbox)

    def ocr(self, img) -> str:  # pragma: no cover - heavy dependency
        """Perform OCR on *img* using ``pytesseract``."""

        return pytesseract.image_to_string(img).strip()

    def is_new_question(self, text: str) -> bool:
        """Return ``True`` if ``text`` differs from the previous one."""

        h = hash_text(text)
        if h == self._last_hash:
            return False
        self._last_hash = h
        return True

    # --- thread interface -------------------------------------------
    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        self._pause.clear()

    def stop(self) -> None:
        self.stop_flag.set()

    def run(self) -> None:  # pragma: no cover - tested via side effects
        while not self.stop_flag.is_set():
            if self._pause.is_set():
                time.sleep(self.cfg.poll_interval)
                continue
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.queue.put(("question", text))
            time.sleep(self.cfg.poll_interval)


__all__ = ["Watcher", "Region", "_mss"]

