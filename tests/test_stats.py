"""Tests for :mod:`quiz_automation.stats`."""

from quiz_automation.stats import Stats
import pytest
from threading import Thread


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


def test_thread_safety() -> None:
    stats = Stats()

    def record_worker() -> None:
        for _ in range(100):
            stats.record(1.0, 2)

    def error_worker() -> None:
        for _ in range(40):
            stats.record_error()

    threads = [Thread(target=record_worker) for _ in range(5)] + [Thread(target=error_worker) for _ in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert stats.questions_answered == 5 * 100
    assert stats.errors == 5 * 40
    assert stats.average_time == pytest.approx(1.0)
    assert stats.average_tokens == pytest.approx(2.0)

