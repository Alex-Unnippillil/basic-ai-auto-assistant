from quiz_automation.stats import Stats


def test_stats_summary():
    s = Stats()
    s.record_ocr(1.0)
    s.record_ocr(2.0)
    s.record_model(0.5)
    s.record_model(1.5)
    s.inc_questions()
    s.inc_questions()
    summary = s.summary()
    assert summary["questions"] == 2
    assert summary["ocr_avg"] == 1.5
    assert summary["model_avg"] == 1.0
