import time
from queue import Queue

import pytest

from quiz_automation import watcher as watcher_module
from quiz_automation.config import Settings
from quiz_automation.watcher import Watcher
from quiz_automation.region_selector import RegionSelector


class DummyMSS:
    def grab(self, bbox):
        return [[0]]  # minimal placeholder


def test_watcher_is_new_question(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(watcher_module, "_mss", lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})())
    cfg = Settings()
    w = Watcher((0, 0, 1, 1), Queue(), cfg)
    assert w.is_new_question("Q1") is True
    assert w.is_new_question("Q1") is False


def test_watcher_emits_event(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(watcher_module, "_mss", lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})())
    cfg = Settings()
    q: Queue = Queue()
    w = Watcher((0, 0, 1, 1), q, cfg)
    monkeypatch.setattr(w, "capture", lambda: "img")
    monkeypatch.setattr(w, "ocr", lambda img: "text")
    monkeypatch.setattr(w, "is_new_question", lambda text: True)

    def fake_sleep(_):
        w.stop_flag.set()

    monkeypatch.setattr("quiz_automation.watcher.time.sleep", fake_sleep)
    w.run()
    assert not q.empty()
    event = q.get()
    assert event[0] == "question"


def test_watcher_pause_resume(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(watcher_module, "_mss", lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})())
    cfg = Settings()
    q: Queue = Queue()
    w = Watcher((0, 0, 1, 1), q, cfg)
    monkeypatch.setattr(w, "capture", lambda: "img")
    monkeypatch.setattr(w, "ocr", lambda img: "text")
    monkeypatch.setattr(w, "is_new_question", lambda text: True)
    w.pause()
    w.start()
    time.sleep(0.1)
    assert q.empty()

    def fake_sleep(_):
        w.stop()

    monkeypatch.setattr("quiz_automation.watcher.time.sleep", fake_sleep)
    w.resume()
    w.join()
    assert not q.empty()


def test_watcher_no_event_for_duplicate(monkeypatch):
    """Watcher should not emit events for repeated questions."""
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    cfg = Settings()
    q: Queue = Queue()
    w = Watcher((0, 0, 1, 1), q, cfg)
    monkeypatch.setattr(w, "capture", lambda: "img")
    monkeypatch.setattr(w, "ocr", lambda img: "text")
    monkeypatch.setattr(w, "is_new_question", lambda text: False)

    def fake_sleep(_):
        w.stop_flag.set()

    monkeypatch.setattr("quiz_automation.watcher.time.sleep", fake_sleep)
    w.run()
    assert q.empty()


def test_region_calibration_success(monkeypatch, tmp_path):
    """RegionSelector should compute coordinates from two positions."""
    path = tmp_path / "coords.json"
    selector = RegionSelector(path)
    positions = iter([(10, 20), (50, 80)])
    monkeypatch.setattr("builtins.input", lambda prompt="": None)
    monkeypatch.setattr(
        "quiz_automation.region_selector.pyautogui.position",
        lambda: next(positions),
    )
    region = selector.select("quiz")
    assert region == (10, 20, 40, 60)


def test_region_calibration_failure(monkeypatch, tmp_path):
    """RegionSelector should raise when user does not provide two points."""
    path = tmp_path / "coords.json"
    selector = RegionSelector(path)
    positions = iter([(1, 2)])  # only one point provided
    monkeypatch.setattr("builtins.input", lambda prompt="": None)
    monkeypatch.setattr(
        "quiz_automation.region_selector.pyautogui.position",
        lambda: next(positions),
    )
    with pytest.raises(StopIteration):
        selector.select("quiz")
