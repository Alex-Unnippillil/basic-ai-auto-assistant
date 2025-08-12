from __future__ import annotations

"""OCR backends used by the quiz watcher."""

from typing import Protocol


class OCRBackend(Protocol):
    """Simple callable protocol for OCR backends."""

    def __call__(self, img) -> str:  # pragma: no cover - behaviour depends on backend
        ...


class PytesseractOCR:
    """Default OCR backend using :mod:`pytesseract`.

    The implementation only runs when the callable is invoked so that unit tests
    can provide lightweight stubs.  When dependencies are missing a clear
    ``RuntimeError`` is raised.
    """

    def __init__(self, lang: str | None = None) -> None:
        self.lang = lang

    def __call__(self, img) -> str:  # pragma: no cover - requires optional deps
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore
        except Exception as exc:  # pragma: no cover - exercised via tests
            raise RuntimeError("pytesseract not available") from exc

        # ``mss`` screenshots expose ``rgb`` and ``size`` attributes.  When that
        # shape is detected we convert to a Pillow image; otherwise we assume the
        # caller already supplied a compatible object.
        if hasattr(img, "size") and hasattr(img, "rgb"):
            pil_img = Image.frombytes("RGB", img.size, img.rgb)
        else:  # pragma: no cover - passthrough for already supported objects
            pil_img = img
        return pytesseract.image_to_string(pil_img, lang=self.lang)
