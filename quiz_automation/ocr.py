from __future__ import annotations

"""OCR backends used by the quiz watcher."""

from importlib import import_module
from typing import Any, Callable, Dict, Protocol


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


# -- backend registry ---------------------------------------------------

_BACKENDS: Dict[str, Callable[..., OCRBackend]] = {"pytesseract": PytesseractOCR}


def register_backend(name: str, backend: Callable[..., OCRBackend] | type[OCRBackend]) -> None:
    """Register *backend* under *name*.

    ``backend`` may be a class implementing :class:`OCRBackend` or a callable
    returning such an object.
    """

    _BACKENDS[name] = backend  # type: ignore[assignment]


def get_backend(name: str | None = None, **kwargs: Any) -> OCRBackend:
    """Return an OCR backend from *name*.

    When *name* is ``None`` the default ``pytesseract`` backend is returned.
    If *name* matches a registered backend the associated factory is invoked.
    Otherwise *name* is treated as an import path of the form
    ``'module:qualname'`` or ``'module.qualname'`` and imported dynamically.
    """

    target = name or "pytesseract"
    factory = _BACKENDS.get(target)
    if factory is not None:
        if isinstance(factory, type):
            return factory(**kwargs)  # type: ignore[misc]
        return factory(**kwargs)

    module_name, sep, qualname = target.replace(":", ".").rpartition(".")
    if not sep:
        raise RuntimeError(f"Unknown OCR backend '{target}'")
    try:
        module = import_module(module_name)
        obj = getattr(module, qualname)
    except Exception as exc:
        raise RuntimeError(f"Could not load OCR backend '{target}'") from exc
    if isinstance(obj, type):
        return obj(**kwargs)  # type: ignore[misc]
    if callable(obj):
        return obj(**kwargs)
    raise RuntimeError(f"OCR backend '{target}' is not callable")


__all__ = [
    "OCRBackend",
    "PytesseractOCR",
    "register_backend",
    "get_backend",
]
