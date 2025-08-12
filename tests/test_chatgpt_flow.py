from queue import Queue

import pytest

from quiz_automation.watcher import Watcher
from quiz_automation.config import Settings
from quiz_automation.model_client import LocalModelClient
from quiz_automation.stats import Stats


def test_chatgpt_flow_end_to_end(monkeypatch):
    q: Queue = Queue()
    cfg = Settings()
    w = Watcher((0, 0, 1, 1), q, cfg)
    monkeypatch.setattr(w, "capture", lambda: "img")
    monkeypatch.setattr(w, "ocr", lambda img: "Which fruit is red?")
    monkeypatch.setattr(w, "is_new_question", lambda text: True)
    monkeypatch.setattr("quiz_automation.watcher.time.sleep", lambda _: w.stop())

    w.start()
    w.join()

    assert not q.empty()
    _, img, question = q.get()
    assert img == "img" and question == "Which fruit is red?"

    model = LocalModelClient()
    answer = model.ask(question, ["Apple", "Banana"])

    stats = Stats()
    stats.record(0.5, len(question.split()))

    assert answer == "A"
    assert stats.questions_answered == 1
    assert stats.average_tokens == pytest.approx(len(question.split()))
