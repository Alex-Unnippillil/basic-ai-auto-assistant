"""PySide6 GUI exposing Start, Pause and Stop controls."""
from __future__ import annotations

from queue import Queue
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .config import settings
from .region_selector import select_region
from .watcher import Watcher
from .runner import QuizRunner


class QuizGUI:
    """Tiny GUI to control the quiz automation workflow."""

    def __init__(self, app: Optional[QApplication] = None) -> None:
        self.app = app or QApplication.instance() or QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Quiz Automation")
        layout = QVBoxLayout(self.window)
        self.status = QLabel("Idle")
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        layout.addWidget(self.status)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)

        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)

        self.event_queue: Queue = Queue()
        self.watcher: Optional[Watcher] = None
        self.runner: Optional[QuizRunner] = None

    def start(self) -> None:
        self.status.setText("Running")
        region = select_region()
        self.watcher = Watcher(region, self.event_queue, settings)
        self.watcher.start()
        # Placeholder coordinates for demo purposes; in a real application these
        # would be gathered via the watcher or additional selectors.
        self.runner = QuizRunner(region, (0, 0), region, ["A"], (0, 0))
        self.runner.start()

    def pause(self) -> None:
        self.status.setText("Paused")
        if self.watcher:
            self.watcher.stop_flag.set()
        if self.runner:
            self.runner.stop_flag.set()

    def stop(self) -> None:
        self.status.setText("Stopped")
        if self.watcher:
            self.watcher.stop_flag.set()
            self.watcher.join()
            self.watcher = None
        if self.runner:
            self.runner.stop_flag.set()
            self.runner.join()
            self.runner = None

    def run(self) -> None:  # pragma: no cover - GUI loop
        self.window.show()
        self.app.exec()
