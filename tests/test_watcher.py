from queue import Queue

from quiz_automation.config import Settings
from quiz_automation.watcher import Watcher


class DummyMSS:
    def grab(self, bbox):
        return [[0]]  # minimal placeholder


def test_watcher_is_new_question(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr("quiz_automation.watcher.mss.mss", lambda: DummyMSS())
    cfg = Settings()
    watcher = Watcher((0, 0, 1, 1), Queue(), cfg)
    assert watcher.is_new_question("Q1") is True
    assert watcher.is_new_question("Q1") is False


def test_watcher_emits_event(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr("quiz_automation.watcher.mss.mss", lambda: DummyMSS())
    cfg = Settings()
    q: Queue = Queue()
    watcher = Watcher((0, 0, 1, 1), q, cfg)
    monkeypatch.setattr(watcher, "capture", lambda: "img")
    monkeypatch.setattr(watcher, "ocr", lambda img: "text")
    monkeypatch.setattr(watcher, "is_new_question", lambda text: True)

    def fake_sleep(_):
        watcher.stop_flag.set()

    monkeypatch.setattr("quiz_automation.watcher.time.sleep", fake_sleep)
    watcher.run()
    assert not q.empty()
    event = q.get()
    assert event[0] == "question"
