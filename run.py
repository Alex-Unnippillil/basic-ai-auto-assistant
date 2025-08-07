"""Entry point for running the quiz automation GUI."""
from __future__ import annotations

from quiz_automation.gui import QuizGUI


def main() -> None:
    gui = QuizGUI()
    gui.run()


if __name__ == "__main__":
    main()
