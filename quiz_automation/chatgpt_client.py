"""Minimal OpenAI client wrapper with retry logic."""
from __future__ import annotations

import json
import time
from typing import Optional

from .logger import get_logger

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    get_logger(__name__).warning("openai package not available; ChatGPTClient disabled")

from .config import settings

logger = get_logger(__name__)


class ChatGPTClient:
    """Wrapper around the OpenAI SDK that returns a single-letter answer."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package not available")
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)

    def _completion(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="o4-mini-high",
            input=[
                {"role": "system", "content": "Reply with JSON {'answer':'A|B|C|D'}"},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text

    def ask(self, prompt: str, retries: int = 3) -> str:
        """Return the model's single-letter answer with basic retries."""
        for attempt in range(retries):
            try:
                raw = self._completion(prompt)
                data = json.loads(raw)
                return data["answer"]
            except Exception:
                logger.exception("OpenAI request failed on attempt %s", attempt + 1)
                time.sleep(2**attempt)
        logger.error("Failed to get model response")
        raise RuntimeError("Failed to get model response")
