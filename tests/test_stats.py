from quiz_automation.stats import Stats


def test_stats_records_accuracy():
    s = Stats()
    s.record(True)
    s.record(False)
    assert s.asked == 2
    assert s.correct == 1
    assert abs(s.accuracy - 0.5) < 1e-6
