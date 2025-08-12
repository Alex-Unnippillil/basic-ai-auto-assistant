"""Minimal OpenAI client wrapper with retry logic."""
from __future__ import annotations

import json
import time
import logging
from typing import Optional

try:  # pragma: no cover - optional dependency
    from openai import (
        OpenAI,
        APIError,
        APIConnectionError,
        RateLimitError,
        APITimeoutError,
    )
except ModuleNotFoundError:  # pragma: no cover
    OpenAI = None  # type: ignore
    APIError = APIConnectionError = RateLimitError = APITimeoutError = Exception  # type: ignore

from .config import settings


logger = logging.getLogger(__name__)


class ChatGPTClient:
    """Wrapper around the OpenAI SDK that returns a single-letter answer."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package not available")
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_model

    def _completion(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
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
            except (
                APIError,
                APIConnectionError,
                RateLimitError,
                APITimeoutError,
                json.JSONDecodeError,
            ) as exc:
                logger.warning("Attempt %d/%d failed: %s", attempt + 1, retries, exc)
                time.sleep(2**attempt)
        logger.error("All %d attempts failed", retries)
        raise RuntimeError("Failed to get model response")
