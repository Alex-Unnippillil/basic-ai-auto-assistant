"""Tests for :mod:`quiz_automation.stats`."""

import pytest

pytest.importorskip("pydantic_settings")

from quiz_automation.stats import Stats



def test_record_updates_counts_and_averages() -> None:
    stats = Stats()
    stats.record(1.0, 4)
    stats.record(2.0, 6)

    assert stats.questions_answered == 2
    assert stats.total_time == pytest.approx(3.0)
    assert stats.total_tokens == 10
    # Average of recorded times
    assert stats.average_time == pytest.approx(1.5)
    # Average of recorded token counts
    assert stats.average_tokens == pytest.approx(5.0)


def test_record_error_increments_error_counter() -> None:
    stats = Stats()
    stats.record_error()
    stats.record_error()
    assert stats.errors == 2


