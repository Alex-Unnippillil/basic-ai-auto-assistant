import sqlite3

from quiz_automation import automation
from quiz_automation.logger import Logger


def test_read_chatgpt_response_logs_timeout(monkeypatch, tmp_path):
    """read_chatgpt_response refreshes once and logs timeouts."""

    # Always return blank text so OCR never succeeds
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: "img")
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "")

    # Capture refresh hotkey usage
    hotkeys: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        automation.pyautogui, "hotkey", lambda *keys: hotkeys.append(keys)
    )

    # Speed up polling
    monkeypatch.setattr(automation.time, "sleep", lambda _t: None)

    db = tmp_path / "log.db"
    logger = Logger(str(db))

    text = automation.read_chatgpt_response(
        (0, 0, 1, 1), timeout=0, poll=0, logger=logger
    )
    assert text == ""
    assert hotkeys == [("ctrl", "r")]

    rows = list(sqlite3.connect(db).execute("SELECT action, data FROM events"))
    assert rows[0][0] == "timeout"
    logger.close()


def test_answer_question_via_chatgpt_skips_on_timeout(monkeypatch, tmp_path):
    """Timeouts do not crash the loop and produce no clicks."""

    logger = Logger(str(tmp_path / "log.db"))

    monkeypatch.setattr(automation, "screenshot_region", lambda region: "img")
    monkeypatch.setattr(automation, "send_to_chatgpt", lambda img, box: None)

    # Make read_chatgpt_response always timeout and log
    monkeypatch.setattr(
        automation,
        "read_chatgpt_response",
        lambda region, timeout=0, poll=0, logger=None: (
            logger.log("timeout", "{}".format(region)) if logger else "",
            ""
        )[1],
    )

    monkeypatch.setattr(automation, "_extract_letter", lambda r: r, raising=False)

    clicked: list[int] = []
    monkeypatch.setattr(
        automation,
        "click_option",
        lambda base, idx, offset=40: clicked.append(idx),
    )

    # Simulate loop with two iterations to ensure no crash
    for _ in range(2):
        letter = automation.answer_question_via_chatgpt(
            (0, 0, 1, 1),
            (0, 0),
            (0, 0, 1, 1),
            ["A", "B"],
            (0, 0),
            logger=logger,
        )
        assert letter == ""

    assert clicked == []
    logger.close()
