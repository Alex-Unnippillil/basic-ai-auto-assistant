import logging

from quiz_automation.logger import configure_logger, get_logger
from quiz_automation import automation
from quiz_automation.types import Point, Region


def test_configure_logger_and_format(capsys):
    fmt = "%(levelname)s|%(name)s|%(message)s"
    configure_logger(level=logging.DEBUG, fmt=fmt)
    log = get_logger("quiz_automation.test")
    log.debug("hello")
    assert capsys.readouterr().err.strip() == "DEBUG|quiz_automation.test|hello"


def test_get_logger_defaults_to_caller_module():
    configure_logger()
    log = get_logger()
    assert log.name == __name__


def test_automation_logs_message(monkeypatch, caplog):
    configure_logger(level=logging.INFO, fmt="%(message)s")
    caplog.set_level(logging.INFO, logger="quiz_automation.automation")

    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)
    monkeypatch.setattr(
        automation,
        "read_chatgpt_response",
        lambda region, timeout=20.0, poll_interval=0.5: "Answer B",
    )
    monkeypatch.setattr(automation, "click_option", lambda base, idx, offset=40: None)

    letter = automation.answer_question(
        "img", Point(0, 0), Region(0, 0, 10, 10), ["A", "B"], Point(0, 0)
    )
    assert letter == "B"
    assert "ChatGPT chose B" in caplog.text
