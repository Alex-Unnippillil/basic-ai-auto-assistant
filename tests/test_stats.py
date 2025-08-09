from quiz_automation.stats import Stats


def test_record_and_average():
    stats = Stats()
    stats.record(2.0, 10)
    stats.record(4.0, 20)

    assert stats.questions_answered == 2
    assert stats.errors == 0
    assert stats.average_time == 3.0
    assert stats.average_tokens == 15.0


def test_record_error():
    stats = Stats()
    stats.record_error()
    stats.record_error()

    assert stats.errors == 2
    assert stats.questions_answered == 0
    assert stats.average_time == 0.0
    assert stats.average_tokens == 0.0

