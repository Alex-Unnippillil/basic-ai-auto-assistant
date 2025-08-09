from __future__ import annotations

"""Threaded screen watcher that emits new questions via a queue."""

import threading
import time
from queue import Queue
from typing import Optional, Tuple

from .config import Settings

try:  # pragma: no cover - mss and pytesseract are optional in tests
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from mss import mss  # type: ignore
except Exception:  # pragma: no cover
    mss = None  # type: ignore


def _mss():  # pragma: no cover - helper to allow monkeypatching in tests
    return mss


class Watcher(threading.Thread):
    """Capture a screen region and OCR it periodically."""

    def __init__(self, region: Tuple[int, int, int, int], queue: Queue, cfg: Settings) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self._paused = threading.Event()
        self._last_question: Optional[str] = None

    # ------------------------------------------------------------------
    def capture(self):
        if _mss() is None:  # pragma: no cover - dependency missing
            raise RuntimeError("mss library not available")
        with _mss().mss() as sct:  # type: ignore[call-arg]
            left, top, width, height = self.region
            return sct.grab({"left": left, "top": top, "width": width, "height": height})

    def ocr(self, img) -> str:
        if pytesseract is None:  # pragma: no cover - dependency missing
            raise RuntimeError("pytesseract not available")
        return pytesseract.image_to_string(img)

    def is_new_question(self, text: str) -> bool:
        if text != self._last_question:
            self._last_question = text
            return True
        return False

    # ------------------------------------------------------------------
    def run(self) -> None:  # pragma: no cover - behaviour tested via integration tests
        while not self.stop_flag.is_set():
            if self._paused.is_set():
                time.sleep(0.05)
                continue
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.queue.put(("question", img, text))
            time.sleep(self.cfg.poll_interval)

    # ------------------------------------------------------------------
    def pause(self) -> None:
        self._paused.set()

    def resume(self) -> None:
        self._paused.clear()

    def stop(self) -> None:
        self.stop_flag.set()
        self.resume()
