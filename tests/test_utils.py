import io
import subprocess
import sys
from types import SimpleNamespace

import pytest

from quiz_automation.utils import copy_image_to_clipboard, hash_text, validate_region
from quiz_automation.types import Region


def test_hash_text_consistent():
    assert hash_text("hello") == hash_text("hello")


def test_hash_text_different():
    assert hash_text("hello") != hash_text("world")


class DummyImage:
    def save(self, fp, fmt):  # pragma: no cover - simple helper
        fp.write(b"data")


def test_copy_image_linux(monkeypatch):
    called = {}

    class DummyProc:
        def __init__(self):
            self.stdin = io.BytesIO()

        def wait(self):
            called["wait"] = True

    def fake_popen(cmd, stdin=None, close_fds=True):
        called["cmd"] = cmd
        return DummyProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    assert copy_image_to_clipboard(DummyImage()) is True
    assert called["cmd"][:3] == ["xclip", "-selection", "clipboard"]


def test_copy_image_failure(monkeypatch, caplog):
    class DummyImage:
        def save(self, fp, fmt):  # pragma: no cover - simple helper
            fp.write(b"data")

    def fail_popen(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(subprocess, "Popen", fail_popen)
    monkeypatch.setitem(
        sys.modules,
        "pyperclip",
        SimpleNamespace(copy=lambda *_: (_ for _ in ()).throw(RuntimeError("fail"))),
    )

    with caplog.at_level("ERROR"):
        assert copy_image_to_clipboard(DummyImage()) is False
        assert any("Failed to copy image" in r.message for r in caplog.records)


def test_validate_region_errors():
    with pytest.raises(ValueError):
        validate_region(Region(0, 0, 0, 10))

