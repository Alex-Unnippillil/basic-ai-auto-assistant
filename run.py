"""Command-line interface for quiz automation."""
from __future__ import annotations

import argparse
import logging

from quiz_automation import QuizGUI, Stats
from quiz_automation.runner import QuizRunner
from quiz_automation.config import Settings
from quiz_automation.logger import configure_logger
from quiz_automation.chatgpt_client import ChatGPTClient
from quiz_automation.model_client import LocalModelClient



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
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level for the application",
    )
    parser.add_argument(
        "--config",
        help="Path to a configuration file read by the Settings class",
    )
    parser.add_argument(
        "--backend",
        choices=["chatgpt", "local"],
        default="chatgpt",
        help="Model backend to use",
    )
    args = parser.parse_args(argv)

    level = getattr(logging, args.log_level.upper(), logging.INFO)
    configure_logger(level=level)

    if args.mode == "gui":
        gui = QuizGUI()
        app = getattr(gui, "_app", None)
        if app is not None:
            app.exec()
        else:
            print("PySide6 is not available; running without GUI.")
    else:
        cfg = Settings(_env_file=args.config) if args.config else Settings()
        options = list("ABCD")

        client = ChatGPTClient() if args.backend == "chatgpt" else LocalModelClient()
        runner = QuizRunner(
            cfg.quiz_region,
            cfg.chat_box,
            cfg.response_region,
            options,
            cfg.option_base,
            model_client=client,
            stats=Stats(),
        )
        runner.start()
        try:
            while True:
                runner.join(timeout=1)
                if not runner.is_alive():
                    break
        except KeyboardInterrupt:
            runner.stop()
        finally:
            runner.join()


if __name__ == "__main__":
    main()
