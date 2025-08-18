"""Simple PySide6 based GUI for displaying live quiz metrics."""

from __future__ import annotations

from typing import Optional, Callable, TYPE_CHECKING

from .stats import Stats

if TYPE_CHECKING:  # pragma: no cover - used only for type hints
    from .runner import QuizRunner

try:  # pragma: no cover - optional graphical dependency
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - fall back when Qt is unavailable
    QApplication = QLabel = QPushButton = QVBoxLayout = QWidget = None  # type: ignore


class QuizGUI:
    """Display :class:`Stats` in a lightweight window.

    The widget is intentionally tiny so that unit tests can instantiate it
    without starting a full GUI environment. When PySide6 is not available, the
    class still stores the last rendered text for inspection by tests.
    """

    def __init__(self) -> None:
        """Create the GUI window and underlying Qt widgets."""
        self._app: Optional[QApplication]
        self._label: Optional[QLabel]
        self._last_text: str = ""

        # Callbacks for external control
        self.on_pause: Optional[Callable[[], None]] = None
        self.on_resume: Optional[Callable[[], None]] = None
        self.on_stop: Optional[Callable[[], None]] = None

        # Button references (may remain ``None`` in headless mode)
        self._pause_btn: Optional[QPushButton]
        self._resume_btn: Optional[QPushButton]
        self._stop_btn: Optional[QPushButton]

        if QApplication is None:  # pragma: no cover - headless fallback
            self._app = None
            self._label = None
            self._pause_btn = None
            self._resume_btn = None
            self._stop_btn = None
            return

        self._app = QApplication.instance() or QApplication([])
        self._window = QWidget()
        layout = QVBoxLayout(self._window)
        self._label = QLabel("Ready")
        layout.addWidget(self._label)

        # Control buttons
        self._pause_btn = QPushButton("Pause")
        self._resume_btn = QPushButton("Resume")
        self._stop_btn = QPushButton("Stop")
        self._pause_btn.clicked.connect(self._emit_pause)
        self._resume_btn.clicked.connect(self._emit_resume)
        self._stop_btn.clicked.connect(self._emit_stop)
        layout.addWidget(self._pause_btn)
        layout.addWidget(self._resume_btn)
        layout.addWidget(self._stop_btn)

        self._window.setWindowTitle("Quiz Stats")
        self._window.show()

    def update(self, stats: Stats) -> None:
        """Refresh the GUI with the latest *stats*."""
        text = (
            f"Questions: {stats.questions_answered} | "
            f"Avg Time: {stats.average_time:.2f}s | "
            f"Avg Tokens: {stats.average_tokens:.1f} | "
            f"Errors: {stats.errors}"
        )
        self._last_text = text

        if self._label is not None:  # pragma: no branch - only if GUI is active
            self._label.setText(text)
            # ``processEvents`` keeps the UI responsive during tests without a
            # full event loop running.
            assert self._app is not None  # for type checkers
            self._app.processEvents()

    @property
    def last_text(self) -> str:
        """Return the most recently rendered text."""
        return self._last_text

    # ------------------------------------------------------------------
    # Button signal emitters
    def _emit_pause(self) -> None:
        if self.on_pause is not None:
            self.on_pause()

    def _emit_resume(self) -> None:
        if self.on_resume is not None:
            self.on_resume()

    def _emit_stop(self) -> None:
        if self.on_stop is not None:
            self.on_stop()

    # ------------------------------------------------------------------
    # Convenience helpers
    def connect_runner(self, runner: "QuizRunner") -> None:
        """Wire GUI controls to *runner* methods."""
        self.on_pause = runner.pause
        self.on_resume = runner.resume
        self.on_stop = runner.stop
