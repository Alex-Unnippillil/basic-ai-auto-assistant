"""Command-line interface for quiz automation."""
from __future__ import annotations

import argparse
import logging

from quiz_automation import QuizGUI
from quiz_automation.runner import QuizRunner
from quiz_automation.config import Settings, settings as global_settings
from quiz_automation.logger import configure_logger
from quiz_automation.chatgpt_client import ChatGPTClient
from quiz_automation.model_client import LocalModelClient
from quiz_automation.stats import Stats



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
        "--max-questions",
        type=int,
        help="Stop after answering this many questions",
    )
    parser.add_argument(
        "--backend",
        choices=["chatgpt", "local"],
        default="chatgpt",
        help="Model backend to use for answering questions",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Sampling temperature for the ChatGPT model",
    )
    args = parser.parse_args(argv)

    if args.temperature is not None and args.temperature < 0:
        parser.error("--temperature must be non-negative")

    level = getattr(logging, args.log_level.upper(), logging.INFO)
    configure_logger(level=level)

    if args.mode == "gui":
        gui = QuizGUI()
        cfg = Settings(_env_file=args.config) if args.config else Settings()
        if args.temperature is not None:
            cfg.temperature = args.temperature
            global_settings.temperature = args.temperature
        options = list("ABCD")
        stats = Stats()
        model_client = (
            ChatGPTClient() if args.backend == "chatgpt" else LocalModelClient()
        )
        runner = QuizRunner(
            cfg.quiz_region,
            cfg.chat_box,
            cfg.response_region,
            options,
            cfg.option_base,
            gui=gui,
            model_client=model_client,
            stats=stats,
        )
        runner.start()
        app = getattr(gui, "_app", None)
        try:
            if app is not None:
                app.exec()
            else:
                print("PySide6 is not available; running without GUI.")
                while True:
                    runner.join(timeout=1)
                    if not runner.is_alive():
                        break
                    if (
                        args.max_questions is not None
                        and stats.questions_answered >= args.max_questions
                    ):
                        runner.stop()
        except KeyboardInterrupt:
            pass
        finally:
            runner.stop()
            runner.join()
    else:
        cfg_kwargs = {"_env_file": args.config} if args.config else {}
        if args.temperature is not None:
            cfg_kwargs["temperature"] = args.temperature
        cfg = Settings(**cfg_kwargs)
        if args.temperature is not None:
            cfg.temperature = args.temperature
            global_settings.temperature = args.temperature
        options = list("ABCD")
        stats = Stats()
        model_client = (
            ChatGPTClient() if args.backend == "chatgpt" else LocalModelClient()
        )

        runner = QuizRunner(
            cfg.quiz_region,
            cfg.chat_box,
            cfg.response_region,
            options,
            cfg.option_base,

            model_client=model_client,
            stats=stats,
        )
        runner.start()
        try:
            while True:
                runner.join(timeout=1)
                if not runner.is_alive():
                    break
                if (
                    args.max_questions is not None
                    and stats.questions_answered >= args.max_questions
                ):
                    runner.stop()
        except KeyboardInterrupt:
            runner.stop()
        finally:
            runner.join()


if __name__ == "__main__":
    main()
