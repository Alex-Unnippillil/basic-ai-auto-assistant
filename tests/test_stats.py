"""Tests for the :mod:`quiz_automation.stats` module."""

from quiz_automation.stats import Stats


def test_record_and_averages():
    """Recording questions updates counters and averages correctly."""

    s = Stats()
    s.record(2.0, 10)
    s.record(4.0, 20)

    assert s.questions_answered == 2
    assert s.question_times == [2.0, 4.0]
    assert s.token_counts == [10, 20]
    assert s.average_time == 3.0
    assert s.average_tokens == 15.0


def test_record_error_increments_errors():
    s = Stats()
    s.record_error()
    assert s.errors == 1

