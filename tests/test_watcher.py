import logging
import time
from queue import Queue

import pytest

pytest.importorskip("pydantic_settings")

import quiz_automation.ocr as ocr_module
from quiz_automation import watcher as watcher_module
from quiz_automation.config import Settings
from quiz_automation.ocr import PytesseractOCR
from quiz_automation.types import Region
from quiz_automation.watcher import Watcher


class DummyMSS:
    def grab(self, bbox):
        return [[0]]  # minimal placeholder


def test_default_ocr_backend(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    cfg = Settings()
    w = Watcher(Region(0, 0, 1, 1), Queue(), cfg)
    assert isinstance(w.ocr_backend, PytesseractOCR)


def test_configured_ocr_backend(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    monkeypatch.setattr(ocr_module, "_BACKENDS", dict(ocr_module._BACKENDS))

    class DummyBackend:
        def __init__(self, lang=None):
            assert lang is None

        def __call__(self, img):  # pragma: no cover - simple stub
            return "dummy"

    ocr_module.register_backend("dummy", DummyBackend)
    cfg = Settings(ocr_backend="dummy")
    w = Watcher((0, 0, 1, 1), Queue(), cfg)
    assert isinstance(w.ocr_backend, DummyBackend)


def test_watcher_is_new_question(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    cfg = Settings()
    w = Watcher(Region(0, 0, 1, 1), Queue(), cfg)
    assert w.is_new_question("Q1") is True
    assert w.is_new_question("Q1") is False


def test_watcher_emits_event(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    cfg = Settings()
    q: Queue = Queue()
    w = Watcher(Region(0, 0, 1, 1), q, cfg, ocr=lambda img: "text")
    monkeypatch.setattr(w, "capture", lambda: "img")
    monkeypatch.setattr(w, "is_new_question", lambda text: True)

    def fake_sleep(_):
        w.stop()

    monkeypatch.setattr("quiz_automation.watcher.time.sleep", fake_sleep)
    w.run()
    assert not q.empty()
    event = q.get()
    assert event[0] == "question"


def test_watcher_pause_resume(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        watcher_module,
        "_mss",
        lambda: type("S", (), {"mss": lambda self=None: DummyMSS()})(),
    )
    cfg = Settings()
    q: Queue = Queue()
    w = Watcher(Region(0, 0, 1, 1), q, cfg, ocr=lambda img: "text")
    monkeypatch.setattr(w, "capture", lambda: "img")
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


def test_capture_missing_mss_logs_and_raises(monkeypatch, caplog):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(watcher_module, "mss", None, raising=False)
    cfg = Settings()
    w = Watcher(Region(0, 0, 1, 1), Queue(), cfg)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="mss"):
            w.capture()
    assert "Failed to obtain mss instance" in caplog.text
