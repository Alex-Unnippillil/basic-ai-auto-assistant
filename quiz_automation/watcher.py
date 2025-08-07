"""Simple background watcher thread used by the GUI.

The real project might monitor the screen for changes and push events into an
output queue.  For the purposes of the tests we only need a lightweight thread
that respects a stop flag and periodically posts a tick event.
"""
from __future__ import annotations

import threading
import time
from queue import Queue
from typing import Tuple

from .config import Settings


class Watcher(threading.Thread):
    """Periodically place a tick event into a queue until stopped."""

    def __init__(self, region: Tuple[int, int, int, int], queue: Queue, settings: Settings) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.queue = queue
        self.settings = settings
        self.stop_flag = threading.Event()

    def run(self) -> None:  # pragma: no cover - trivial loop
        while not self.stop_flag.is_set():
            self.queue.put({"region": self.region})
            time.sleep(self.settings.poll_interval)
