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
    def convert(self, mode):  # pragma: no cover - simple helper
        return self

    def save(self, fp, fmt=None, **_: object):  # pragma: no cover - simple helper
        fp.write(b"x" * 20)


def test_copy_image_windows(monkeypatch):
    calls = []

    def open_clipboard():
        calls.append("open")

    def close_clipboard():
        calls.append("close")

    def empty_clipboard():
        calls.append("empty")

    def set_clipboard_data(fmt, data):
        calls.append("set")

    fake = SimpleNamespace(
        CF_DIB=1,
        OpenClipboard=open_clipboard,
        CloseClipboard=close_clipboard,
        EmptyClipboard=empty_clipboard,
        SetClipboardData=set_clipboard_data,
    )

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setitem(sys.modules, "win32clipboard", fake)

    assert copy_image_to_clipboard(DummyImage()) is True
    assert calls == ["open", "empty", "set", "close"]


def test_copy_image_macos(monkeypatch):
    calls: dict[str, object] = {}

    class DummyStdin(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            calls["stdin_closed"] = True
            self.close()

    class DummyProc:
        def __init__(self):
            self.stdin = DummyStdin()

        def __enter__(self):
            calls["enter"] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            calls["exit"] = True
            self.wait()

        def wait(self):
            calls["wait"] = True

    def fake_popen(cmd, stdin=None, close_fds=True):
        calls["cmd"] = cmd
        return DummyProc()

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    assert copy_image_to_clipboard(DummyImage()) is True
    assert calls["cmd"] == ["pbcopy"]
    assert calls["wait"] is True and calls.get("stdin_closed") is True


def test_copy_image_linux(monkeypatch):
    calls: dict[str, object] = {}

    class DummyStdin(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            calls["stdin_closed"] = True
            self.close()

    class DummyProc:
        def __init__(self):
            self.stdin = DummyStdin()

        def __enter__(self):
            calls["enter"] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            calls["exit"] = True
            self.wait()

        def wait(self):
            calls["wait"] = True

    def fake_popen(cmd, stdin=None, close_fds=True):
        calls["cmd"] = cmd
        return DummyProc()

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    assert copy_image_to_clipboard(DummyImage()) is True
    assert calls["cmd"][:3] == ["xclip", "-selection", "clipboard"]
    assert calls["wait"] is True and calls.get("stdin_closed") is True


def test_copy_image_fallback(monkeypatch):
    def fail_popen(*args, **kwargs):
        raise OSError("boom")

    captured: dict[str, str] = {}

    def fake_copy(data):
        captured["data"] = data

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(subprocess, "Popen", fail_popen)
    monkeypatch.setitem(sys.modules, "pyperclip", SimpleNamespace(copy=fake_copy))

    assert copy_image_to_clipboard(DummyImage()) is True
    assert "data" in captured


def test_copy_image_failure(monkeypatch, caplog):
    def fail_popen(*args, **kwargs):
        raise OSError("boom")

    def fail_copy(data):
        raise RuntimeError("fail")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(subprocess, "Popen", fail_popen)
    monkeypatch.setitem(sys.modules, "pyperclip", SimpleNamespace(copy=fail_copy))

    with caplog.at_level("ERROR"):
        assert copy_image_to_clipboard(DummyImage()) is False
        assert any("Failed to copy image" in r.message for r in caplog.records)


def test_validate_region_errors():
    with pytest.raises(ValueError):
        validate_region(Region(0, 0, 0, 10))

