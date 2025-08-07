import sqlite3

from quiz_automation.logger import Logger


def test_logger_writes_entry(tmp_path):
    db = tmp_path / "test.db"
    logger = Logger(str(db))
    logger.log("action", "data")
    rows = list(sqlite3.connect(db).execute("SELECT action, data FROM events"))
    assert rows[0] == ("action", "data")
    logger.close()
