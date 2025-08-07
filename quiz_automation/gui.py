"""PySide6 GUI exposing Start, Pause and Stop controls."""
from __future__ import annotations

from queue import Queue
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from .config import settings
from .region_selector import select_region
from .watcher import Watcher
from .stats import Stats


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
        self.stats = Stats()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_status)

    def start(self) -> None:
        if self.watcher and not self.watcher.is_alive():
            self.watcher = None
        if self.watcher:
            self.status.setText("Running")
            self.watcher.resume()
        else:
            self.status.setText("Running")
            region = select_region()
            self.watcher = Watcher(region, self.event_queue, settings)
            self.watcher.start()
        self.timer.start()

    def pause(self) -> None:
        self.status.setText("Paused")
        if self.watcher:
            self.watcher.pause()

    def stop(self) -> None:
        self.status.setText("Stopped")
        if self.watcher:
            self.watcher.stop()
            self.watcher.join()
            self.watcher = None
        self.timer.stop()

    def update_status(self) -> None:
        summary = self.stats.summary()
        self.status.setText(
            f"Q:{int(summary['questions'])} ocr:{summary['ocr_avg']:.3f}s model:{summary['model_avg']:.3f}s"
        )

    def run(self) -> None:  # pragma: no cover - GUI loop
        self.window.show()
        self.app.exec()
