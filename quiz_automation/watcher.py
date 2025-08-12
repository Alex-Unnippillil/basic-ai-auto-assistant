from __future__ import annotations

"""Monitor the screen for new quiz questions and emit events."""

import logging
import threading
import time
from queue import Queue

from .config import Settings
from .ocr import OCRBackend, PytesseractOCR
from .utils import hash_text
from .types import Region

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from mss import mss
except Exception:  # pragma: no cover
    mss = None  # type: ignore


def _mss():  # pragma: no cover - tiny wrapper for easier monkeypatching
    if mss is None:
        raise RuntimeError("mss not available")
    return mss


class Watcher(threading.Thread):
    """Background thread that polls the screen for new questions."""

    def __init__(
        self,
        region: Region,
        queue: Queue,
        cfg: Settings,
        ocr: OCRBackend | None = None,
    ) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self._last_hash: str | None = None
        self.ocr_backend = ocr or PytesseractOCR()

    # -- basic helpers -------------------------------------------------
    def capture(self):
        try:
            mss_module = _mss()
        except Exception as exc:
            logger.exception("Failed to obtain mss instance")
            raise RuntimeError("Screen capture requires the 'mss' package") from exc
        return mss_module.mss().grab(self.region.as_tuple())

    def ocr(self, img) -> str:  # pragma: no cover - behaviour provided by backend
        return self.ocr_backend(img)

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
