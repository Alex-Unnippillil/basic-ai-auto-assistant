"""Tests for database persistence utilities."""

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from quiz_automation.persistence import Base, Question, SessionStat
from quiz_automation.stats import Stats


def test_stats_record_persists_to_database() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        stats = Stats(db_session=db)
        stats.record(1.0, 10)
        stats.record(2.0, 20)
        stats.record_error()

        questions = db.query(Question).all()
        assert len(questions) == 2

        stat = db.get(SessionStat, 1)
        assert stat is not None
        assert stat.questions_answered == 2
        assert stat.total_time == pytest.approx(3.0)
        assert stat.total_tokens == 30
        assert stat.errors == 1
