"""Command-line interface for quiz automation."""
from __future__ import annotations

import argparse
import os
import time

from quiz_automation.gui import QuizGUI
from quiz_automation.runner import QuizRunner


def _parse_int_tuple(value: str, length: int) -> tuple[int, ...]:
    parts = value.split(",")
    if len(parts) != length:
        raise argparse.ArgumentTypeError(f"expected {length} comma separated integers")
    try:
        return tuple(int(p) for p in parts)
    except ValueError as exc:  # pragma: no cover - argparse converts to SystemExit
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_options(value: str) -> list[str]:
    parts = value.split(",") if "," in value else list(value)
    opts = [p.strip() for p in parts if p.strip()]
    if not opts:
        raise argparse.ArgumentTypeError("no options specified")
    return opts


def main(argv: list[str] | None = None) -> None:
    """Run the quiz automation tool.

    Parameters
    ----------
    argv:
        Optional list of command line arguments for testing purposes.
    """
    default_quiz_region = _parse_int_tuple(os.getenv("QUIZ_REGION", "100,100,600,400"), 4)
    default_chatgpt_box = _parse_int_tuple(os.getenv("CHATGPT_BOX", "800,900"), 2)
    default_response_region = _parse_int_tuple(os.getenv("RESPONSE_REGION", "100,550,600,150"), 4)
    default_option_base = _parse_int_tuple(os.getenv("OPTION_BASE", "100,520"), 2)
    default_options = _parse_options(os.getenv("OPTIONS", "ABCD"))

    parser = argparse.ArgumentParser(description="Quiz automation entry point")
    parser.add_argument(
        "--mode",
        choices=["gui", "headless"],
        default="gui",
        help="Choose whether to launch the GUI or run in headless mode.",
    )
    parser.add_argument(
        "--quiz-region",
        type=lambda s: _parse_int_tuple(s, 4),
        default=default_quiz_region,
        help="Question capture region x,y,width,height",
    )
    parser.add_argument(
        "--chatgpt-box",
        type=lambda s: _parse_int_tuple(s, 2),
        default=default_chatgpt_box,
        help="ChatGPT input box coordinates x,y",
    )
    parser.add_argument(
        "--response-region",
        type=lambda s: _parse_int_tuple(s, 4),
        default=default_response_region,
        help="Region to OCR responses x,y,width,height",
    )
    parser.add_argument(
        "--option-base",
        type=lambda s: _parse_int_tuple(s, 2),
        default=default_option_base,
        help="Coordinates of first answer option x,y",
    )
    parser.add_argument(
        "--options",
        type=_parse_options,
        default=default_options,
        help="Answer option letters, e.g. ABCD or A,B,C,D",
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
        runner = QuizRunner(
            args.quiz_region,
            args.chatgpt_box,
            args.response_region,
            args.options,
            args.option_base,
        )
        runner.start()
        try:
            while runner.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            runner.stop()
        runner.join()


if __name__ == "__main__":
    main()
