"""Tests for :mod:`quiz_automation.stats`."""

from quiz_automation.stats import Stats
import pytest
from concurrent.futures import ThreadPoolExecutor


def test_record_updates_counts_and_averages() -> None:
    stats = Stats()
    stats.record(1.0, 4)
    stats.record(2.0, 6)

    assert stats.questions_answered == 2
    # Average of [1.0, 2.0]
    assert stats.average_time == pytest.approx(1.5)
    # Average of [4, 6]
    assert stats.average_tokens == pytest.approx(5.0)


def test_record_error_increments_error_counter() -> None:
    stats = Stats()
    stats.record_error()
    stats.record_error()
    assert stats.errors == 2


def test_concurrent_updates_thread_safe() -> None:
    stats = Stats()

    def do_record() -> None:
        stats.record(1.0, 1)

    def do_error() -> None:
        stats.record_error()

    total_records = 20
    total_errors = 10

    with ThreadPoolExecutor(max_workers=8) as executor:
        for _ in range(total_records):
            executor.submit(do_record)
        for _ in range(total_errors):
            executor.submit(do_error)

    assert stats.questions_answered == total_records
    assert stats.errors == total_errors
    assert stats.average_time == pytest.approx(1.0)
    assert stats.average_tokens == pytest.approx(1.0)

