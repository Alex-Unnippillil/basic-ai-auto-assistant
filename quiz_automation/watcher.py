"""Screen region watcher that captures screenshots and performs OCR."""
from __future__ import annotations

import importlib
import time
from queue import Queue
from threading import Event, Thread
from typing import Tuple

from .config import Settings
from .utils import hash_text, validate_region


def _mss():
    try:  # pragma: no cover
        return importlib.import_module("mss")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("mss is required") from exc


def _np():
    try:  # pragma: no cover
        return importlib.import_module("numpy")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("numpy is required") from exc


def _pytesseract():
    try:  # pragma: no cover
        return importlib.import_module("pytesseract")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pytesseract is required") from exc


def _cv2():
    try:  # pragma: no cover
        return importlib.import_module("cv2")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("opencv-python is required") from exc


class Watcher(Thread):
    """Background thread that polls a region for new questions."""

    def __init__(self, region: Tuple[int, int, int, int], event_queue: Queue, cfg: Settings):
        super().__init__(daemon=True)
        validate_region(region)
        self.region = region
        self.event_queue = event_queue
        self.cfg = cfg
        self.stop_flag = Event()
        self._running = Event()
        self._running.set()
        self.last_hash = ""
        self.sct = _mss().mss()

    def capture(self):
        """Capture the configured region as a numpy array."""
        np = _np()
        left, top, width, height = self.region
        bbox = {"left": left, "top": top, "width": width, "height": height}
        img = np.array(self.sct.grab(bbox))
        return img

    @staticmethod
    def preprocess(img):
        """Apply grayscale and adaptive threshold for better OCR."""
        cv2 = _cv2()
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )
        return thresh

    def ocr(self, img) -> str:
        pt = _pytesseract()
        processed = self.preprocess(img)
        return pt.image_to_string(processed)

    def is_new_question(self, text: str) -> bool:
        """Return True if the text is different from the last seen question."""
        h = hash_text(text)
        if h != self.last_hash and text.strip():
            self.last_hash = h
            return True
        return False

    def pause(self) -> None:
        """Pause the watcher loop."""
        self._running.clear()

    def resume(self) -> None:
        """Resume the watcher loop."""
        self._running.set()

    def stop(self) -> None:
        """Signal the watcher loop to terminate."""
        self.stop_flag.set()
        self._running.set()

    def run(self) -> None:  # pragma: no cover - loop control tested separately
        while not self.stop_flag.is_set():
            self._running.wait()
            if self.stop_flag.is_set():
                break
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.event_queue.put(("question", text, img))
            time.sleep(self.cfg.poll_interval)
