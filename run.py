"""Command-line interface for quiz automation."""
from __future__ import annotations

import argparse
import os
from typing import Tuple

from quiz_automation import QuizGUI
from quiz_automation.runner import QuizRunner


def _parse_tuple(env_name: str, default: Tuple[int, ...]) -> Tuple[int, ...]:
    """Parse a comma-separated tuple from an environment variable."""

    raw = os.getenv(env_name)
    if raw:
        try:
            parts = tuple(int(p.strip()) for p in raw.split(","))
            if len(parts) == len(default):
                return parts
        except ValueError:
            pass
    return default


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
        quiz_region = _parse_tuple("QUIZ_REGION", (100, 100, 600, 400))
        chat_box = _parse_tuple("CHAT_BOX", (800, 900))
        response_region = _parse_tuple("RESPONSE_REGION", (100, 550, 600, 150))
        option_base = _parse_tuple("OPTION_BASE", (100, 520))
        options = list("ABCD")
        runner = QuizRunner(quiz_region, chat_box, response_region, options, option_base)
        runner.start()


if __name__ == "__main__":
    main()
