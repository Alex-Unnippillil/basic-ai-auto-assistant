"""Miscellaneous helper functions."""
from __future__ import annotations

import base64
import hashlib
import io
import subprocess
import sys
import logging
from typing import Any

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


def copy_image_to_clipboard(img: Any) -> bool:
    """Copy *img* to the system clipboard using OS-native utilities.

    Falls back to a base64-encoded string via ``pyperclip`` when a native
    clipboard command fails or is unavailable. This keeps tests headless while
    enabling real image pasting on supported platforms. ``True`` is returned on
    success and ``False`` if all strategies fail.
    """

    last_exc: Exception | None = None

    # Windows: use win32clipboard to place a DIB on the clipboard
    if sys.platform.startswith("win"):
        try:  # pragma: no cover - exercised on Windows
            import win32clipboard  # type: ignore

            output = io.BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as exc:  # pragma: no cover - fallback below
            last_exc = exc

    # macOS: pipe PNG data to ``pbcopy``
    if sys.platform == "darwin":
        try:  # pragma: no cover - macOS specific
            proc = subprocess.Popen(
                ["pbcopy"], stdin=subprocess.PIPE, close_fds=True
            )
            img.save(proc.stdin, "PNG")
            proc.stdin.close()
            proc.wait()
            return True
        except Exception as exc:  # pragma: no cover
            last_exc = exc

    # Linux: rely on xclip if present
    try:
        proc = subprocess.Popen(
            ["xclip", "-selection", "clipboard", "-t", "image/png"],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        img.save(proc.stdin, "PNG")
        proc.stdin.close()
        proc.wait()
        return True
    except Exception as exc:  # pragma: no cover - fall back below
        last_exc = exc

    # Fallback: encode PNG as base64 and copy via pyperclip
    try:  # pragma: no cover - lightweight fallback
        import pyperclip  # type: ignore

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pyperclip.copy(base64.b64encode(buf.getvalue()).decode("ascii"))
        return True
    except Exception as exc:  # pragma: no cover - nothing else we can do
        last_exc = exc

    logger.exception("Failed to copy image to clipboard", exc_info=last_exc)
    return False
