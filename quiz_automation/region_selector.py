
from __future__ import annotations

import json
from pathlib import Path

try:  # pragma: no cover - optional dependency
    import pyautogui
except Exception:  # pragma: no cover
    class pyautogui:  # type: ignore
        @staticmethod


class RegionSelector:
        input("Move to top-left and press Enter")
        x1, y1 = pyautogui.position()
        input("Move to bottom-right and press Enter")
        x2, y2 = pyautogui.position()
        region = (x1, y1, x2 - x1, y2 - y1)

