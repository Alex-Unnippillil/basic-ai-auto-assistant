"""Screen region watcher that captures screenshots and performs OCR."""
from __future__ import annotations

import time
from threading import Event, Thread
from typing import Tuple
from queue import Queue

try:  # pragma: no cover - optional heavy deps
    import mss  # type: ignore
except Exception:  # pragma: no cover
    class mss:  # type: ignore
        class mss:  # type: ignore
            def __init__(self, *args, **kwargs):
                pass
            def grab(self, bbox):
                return [[0]]
try:  # pragma: no cover
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    class np:  # type: ignore
        ndarray = object
        @staticmethod
        def array(obj):
            return obj
try:  # pragma: no cover
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    class pytesseract:  # type: ignore
        @staticmethod
        def image_to_string(img):
            return ""
try:  # pragma: no cover
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    class cv2:  # type: ignore
        COLOR_BGRA2GRAY = 0
        ADAPTIVE_THRESH_GAUSSIAN_C = 0
        THRESH_BINARY = 0
        @staticmethod
        def cvtColor(img, code):
            return img
        @staticmethod
        def adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C):
            return src

from .config import Settings
from .utils import hash_text


class Watcher(Thread):
    """Background thread that polls a region for new questions."""

    def __init__(self, region: Tuple[int, int, int, int], event_queue: Queue, cfg: Settings):
        super().__init__(daemon=True)
        self.region = region
        self.event_queue = event_queue
        self.cfg = cfg
        self.stop_flag = Event()
        self.last_hash = ""
        self.sct = mss.mss()

    def capture(self):
        """Capture the configured region as a numpy array."""
        left, top, width, height = self.region
        bbox = {"left": left, "top": top, "width": width, "height": height}
        img = np.array(self.sct.grab(bbox))
        return img

    @staticmethod
    def preprocess(img):
        """Apply grayscale and adaptive threshold for better OCR."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )
        return thresh

    def ocr(self, img) -> str:
        processed = self.preprocess(img)
        return pytesseract.image_to_string(processed)

    def is_new_question(self, text: str) -> bool:
        """Return True if the text is different from the last seen question."""
        h = hash_text(text)
        if h != self.last_hash and text.strip():
            self.last_hash = h
            return True
        return False

    def run(self) -> None:  # pragma: no cover - loop control tested separately
        while not self.stop_flag.is_set():
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.event_queue.put(("question", text, img))
            time.sleep(self.cfg.poll_interval)
