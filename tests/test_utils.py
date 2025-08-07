import io
import subprocess

from quiz_automation.utils import copy_image_to_clipboard, hash_text


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
    copy_image_to_clipboard(DummyImage())
    assert called["cmd"][:3] == ["xclip", "-selection", "clipboard"]
