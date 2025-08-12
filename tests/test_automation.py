import pytest

from quiz_automation import automation


def test_send_to_chatgpt_raises_on_clipboard_failure(monkeypatch):
    monkeypatch.setattr(automation, "copy_image_to_clipboard", lambda img: False)
    with pytest.raises(RuntimeError):
        automation.send_to_chatgpt("img", (0, 0))

