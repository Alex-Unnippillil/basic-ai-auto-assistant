import logging

from quiz_automation.logger import configure_logger, get_logger
from quiz_automation import automation


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
        automation, "read_chatgpt_response", lambda region, timeout=20.0: "Answer B"
    )

    class DummyClicker:
        def __init__(self, base, offset=40):
            pass

        def click(self, index):
            pass

    monkeypatch.setattr(automation, "Clicker", DummyClicker)

    letter = automation.answer_question_via_chatgpt(
        "img", (0, 0), (0, 0, 10, 10), ["A", "B"], (0, 0)
    )
    assert letter == "B"
    assert "ChatGPT chose B" in caplog.text
