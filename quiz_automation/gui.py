"""Simple PySide6 based GUI for displaying live quiz metrics."""

from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - optional graphical dependency
    from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
except Exception:  # pragma: no cover - fall back when Qt is unavailable
    QApplication = QLabel = QVBoxLayout = QWidget = None  # type: ignore

from .stats import Stats


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

        if QApplication is None:  # pragma: no cover - headless fallback
            self._app = None
            self._label = None
            return

        self._app = QApplication.instance() or QApplication([])
        self._window = QWidget()
        layout = QVBoxLayout(self._window)
        self._label = QLabel("Ready")
        layout.addWidget(self._label)
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
