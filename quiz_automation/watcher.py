"""Screen watcher thread that emits OCR'd quiz questions."""
from __future__ import annotations

import logging
import threading
import time
from queue import Queue
from typing import Any, Callable, Optional, Tuple

from .config import Settings
from .utils import hash_text

logger = logging.getLogger(__name__)


# Delayed imports wrapped for ease of monkeypatching in tests

def _mss():  # pragma: no cover - thin wrapper
    import mss

    return mss


def _pytesseract():  # pragma: no cover - thin wrapper
    import pytesseract

    return pytesseract


class Watcher(threading.Thread):
    """Periodically capture a region of the screen and emit new questions."""

    def __init__(
        self,
        region: Tuple[int, int, int, int],
        event_queue: Queue,
        cfg: Settings,
        capture_fn: Optional[Callable[[], Any]] = None,
        ocr_fn: Optional[Callable[[Any], str]] = None,
    ) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = event_queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self.paused = threading.Event()
        self._last_hash: Optional[str] = None

        if capture_fn is not None:
            self.capture = capture_fn
        else:
            sct_module = _mss()
            sct = sct_module.mss()

            def _cap() -> Any:
                return sct.grab(self.region)

            self.capture = _cap

        if ocr_fn is not None:
            self.ocr = ocr_fn
        else:
            def _ocr(img: Any) -> str:
                return _pytesseract().image_to_string(img)

            self.ocr = _ocr

    # ------------------------------------------------------------------
    def is_new_question(self, text: str) -> bool:
        """Return ``True`` if *text* has not been seen before."""

        digest = hash_text(text)
        if digest == self._last_hash:
            return False
        self._last_hash = digest
        return True

    # ------------------------------------------------------------------
    def run(self) -> None:
        while not self.stop_flag.is_set():
            if self.paused.is_set():
                time.sleep(self.cfg.poll_interval)
                continue

            try:
                img = self.capture()
                text = self.ocr(img)
            except Exception as exc:  # pragma: no cover - safety net
                logger.debug("capture/ocr failed: %s", exc)
                time.sleep(self.cfg.poll_interval)
                continue

            if self.is_new_question(text):
                self.queue.put(("question", text))

            time.sleep(self.cfg.poll_interval)

    # ------------------------------------------------------------------
    def pause(self) -> None:
        self.paused.set()

    def resume(self) -> None:
        self.paused.clear()

    def stop(self) -> None:
        self.stop_flag.set()
