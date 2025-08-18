"""Tests for :mod:`quiz_automation.stats`."""

import pytest
from threading import Thread

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


def test_thread_safe_updates_with_multiple_threads() -> None:
    """Ensure concurrent updates are aggregated correctly."""
    stats = Stats()

    record_inputs = [(1.0, 10), (2.0, 20), (3.0, 30)]
    error_threads = 4

    threads = [Thread(target=stats.record, args=ri) for ri in record_inputs]
    threads.extend(Thread(target=stats.record_error) for _ in range(error_threads))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert stats.questions_answered == len(record_inputs)
    assert stats.total_time == pytest.approx(sum(d for d, _ in record_inputs))
    assert stats.total_tokens == sum(t for _, t in record_inputs)
    assert stats.errors == error_threads



