import json
import sqlite3

from quiz_automation.logger import Logger


def test_logger_writes_entry(tmp_path):
    db = tmp_path / "test.db"
    logger = Logger(str(db))
    logger.log("action", value=1)
    rows = list(sqlite3.connect(db).execute("SELECT action, data FROM events"))
    assert rows[0][0] == "action"
    assert json.loads(rows[0][1]) == {"value": 1}
    logger.close()
