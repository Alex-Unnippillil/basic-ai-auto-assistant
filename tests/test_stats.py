from quiz_automation.stats import Stats


def test_stats_summary_and_cache():
    s = Stats()
    s.record_ocr(1.0)
    s.record_model(0.5)
    s.record_question(1.2)
    s.record_tokens(10)
    s.record_error()
    s.cache_store("question", "B")
    assert s.cache_lookup("question") == "B"
    summary = s.summary()
    assert summary["questions"] == 1
    assert summary["ocr_avg"] == 1.0
    assert summary["model_avg"] == 0.5
    assert summary["question_avg"] == 1.2
    assert summary["tokens"] == 10.0
    assert summary["errors"] == 1.0
