"""Miscellaneous helper functions."""
from __future__ import annotations

import hashlib


def hash_text(text: str) -> str:
    """Return a SHA256 hash for *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
