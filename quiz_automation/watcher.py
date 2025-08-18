"""Monitor the screen for new quiz questions and emit events."""

from __future__ import annotations

import logging
import threading
import time
from queue import Queue

from .config import Settings
from .ocr import OCRBackend, get_backend
from .types import Region
from .utils import hash_text

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import mss
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
        """Initialize the watcher thread."""
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.cfg = cfg
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self._last_hash: str | None = None
        self.ocr_backend = ocr or get_backend(cfg.ocr_backend)

    # -- basic helpers -------------------------------------------------
    def capture(self):
        """Capture the configured screen region."""
        try:
            mss_module = _mss()
        except Exception as exc:
            logger.exception("Failed to obtain mss instance")
            raise RuntimeError("Screen capture requires the 'mss' package") from exc
        bbox = {
            "left": self.region.left,
            "top": self.region.top,
            "width": self.region.width,
            "height": self.region.height,
        }
        return mss_module.mss().grab(bbox)

    def ocr(self, img) -> str:  # pragma: no cover - behaviour provided by backend
        """Return OCR text for *img* using the configured backend."""
        return self.ocr_backend(img)

    def is_new_question(self, text: str) -> bool:
        """Return ``True`` if *text* differs from the previous question."""
        current = hash_text(text)
        if current != self._last_hash:
            self._last_hash = current
            return True
        return False

    # -- thread control ------------------------------------------------
    def stop(self) -> None:
        """Signal the watcher thread to stop."""
        self.stop_flag.set()

    def pause(self) -> None:
        """Pause screen polling."""
        self.pause_flag.set()

    def resume(self) -> None:
        """Resume screen polling."""
        self.pause_flag.clear()

    # -- main loop -----------------------------------------------------
    def run(self) -> None:  # pragma: no cover - behaviour exercised in tests
        """Run the watcher loop until stopped."""
        while not self.stop_flag.is_set():
            if self.pause_flag.is_set():
                time.sleep(self.cfg.poll_interval)
                continue
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.queue.put(("question", img, text))
            time.sleep(self.cfg.poll_interval)
