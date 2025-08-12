"""Tests for :mod:`quiz_automation.stats`."""

from quiz_automation.stats import Stats
import pytest
import threading


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


def test_threaded_updates_and_reads() -> None:
    stats = Stats()
    iterations = 1000

    def record_worker() -> None:
        for _ in range(iterations):
            stats.record(1.0, 10)

    def error_worker() -> None:
        for _ in range(iterations):
            stats.record_error()

    def reader_worker() -> None:
        for _ in range(iterations):
            _ = stats.average_time
            _ = stats.average_tokens

    threads = [threading.Thread(target=record_worker) for _ in range(5)]
    threads += [threading.Thread(target=error_worker) for _ in range(3)]
    threads += [threading.Thread(target=reader_worker) for _ in range(2)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert stats.questions_answered == 5 * iterations
    assert stats.errors == 3 * iterations
    assert stats.average_time == pytest.approx(1.0)
    assert stats.average_tokens == pytest.approx(10.0)

