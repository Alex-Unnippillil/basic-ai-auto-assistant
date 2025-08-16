"""Miscellaneous helper functions."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import logging
import subprocess
import sys
from typing import Any, Iterator

from .types import Region


logger = logging.getLogger(__name__)


def hash_text(text: str) -> str:
    """Return a SHA256 hash for *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_region(region: Region) -> None:
    """Ensure *region* has positive width and height."""

    _left, _top, width, height = region
    if width <= 0 or height <= 0:
        raise ValueError("Region width and height must be positive")


@contextlib.contextmanager
def _open_win_clipboard(win32clipboard: Any) -> Iterator[Any]:
    """Context manager that opens and closes the Windows clipboard."""
    win32clipboard.OpenClipboard()
    try:
        yield win32clipboard
    finally:  # pragma: no cover - housekeeping
        win32clipboard.CloseClipboard()


def _copy_windows(img: Any) -> bool:
    import win32clipboard  # pragma: no cover - Windows only

    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    with _open_win_clipboard(win32clipboard) as clip:
        clip.EmptyClipboard()
        clip.SetClipboardData(clip.CF_DIB, data)
    return True


def _copy_macos(img: Any) -> bool:
    with subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True) as proc:
        stdin = proc.stdin
        assert stdin is not None
        with stdin:
            img.save(stdin, "PNG")
    return True


def _copy_linux(img: Any) -> bool:
    with subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-t", "image/png"],
        stdin=subprocess.PIPE,
        close_fds=True,
    ) as proc:
        stdin = proc.stdin
        assert stdin is not None
        with stdin:
            img.save(stdin, "PNG")
    return True


def _copy_fallback(img: Any) -> bool:
    import pyperclip  # pragma: no cover - third-party utility

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    pyperclip.copy(base64.b64encode(buf.getvalue()).decode("ascii"))
    return True


def copy_image_to_clipboard(img: Any) -> bool:
    """Copy *img* to the system clipboard using OS-native utilities.

    Falls back to a base64-encoded string via ``pyperclip`` when a native
    clipboard command fails or is unavailable. This keeps tests headless while
    enabling real image pasting on supported platforms. ``True`` is returned on
    success and ``False`` if all strategies fail.
    """

    last_exc: Exception | None = None

    if sys.platform.startswith("win"):
        try:
            return _copy_windows(img)
        except Exception as exc:  # pragma: no cover - exercised on Windows
            last_exc = exc

    if sys.platform == "darwin":
        try:
            return _copy_macos(img)
        except Exception as exc:  # pragma: no cover - macOS specific
            last_exc = exc

    try:
        return _copy_linux(img)
    except Exception as exc:
        last_exc = exc

    try:
        return _copy_fallback(img)
    except Exception as exc:  # pragma: no cover - nothing else we can do
        last_exc = exc

    logger.exception("Failed to copy image to clipboard", exc_info=last_exc)
    return False
