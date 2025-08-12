"""Command-line interface for quiz automation."""
from __future__ import annotations

import argparse

from quiz_automation import QuizGUI
from quiz_automation.config import Settings
from quiz_automation.runner import QuizRunner


def main(argv: list[str] | None = None) -> None:
    """Run the quiz automation tool.

    Parameters
    ----------
    argv:
        Optional list of command line arguments for testing purposes.
    """
    parser = argparse.ArgumentParser(description="Quiz automation entry point")
    parser.add_argument(
        "--mode",
        choices=["gui", "headless"],
        default="gui",
        help="Choose whether to launch the GUI or run in headless mode.",
    )
    args = parser.parse_args(argv)

    if args.mode == "gui":
        gui = QuizGUI()
        app = getattr(gui, "_app", None)
        if app is not None:
            app.exec()
        else:
            print("PySide6 is not available; running without GUI.")
    else:
        cfg = Settings()
        options = list("ABCD")
        runner = QuizRunner(
            cfg.quiz_region, cfg.chat_box, cfg.response_region, options, cfg.option_base
        )
        runner.start()


if __name__ == "__main__":
    main()
