"""Minimal OpenAI client wrapper with retry logic."""
from __future__ import annotations

import time
from typing import List, Literal, Optional

from pydantic import BaseModel, ValidationError

try:  # pragma: no cover - optional dependency
    from openai import (
        APITimeoutError,
        APIConnectionError,
        RateLimitError,
        OpenAI,
    )
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    APITimeoutError = APIConnectionError = RateLimitError = ()  # type: ignore

from .config import settings
from .model_client import ModelClientProtocol


class QuizAnswer(BaseModel):
    """Expected schema for quiz answers."""

    answer: Literal["A", "B", "C", "D"]

if isinstance(APITimeoutError, type):
    TRANSIENT_ERRORS = (APITimeoutError, APIConnectionError, RateLimitError, TimeoutError, ConnectionError)
else:  # pragma: no cover - openai not installed
    TRANSIENT_ERRORS = (TimeoutError, ConnectionError)


class ChatGPTClient(ModelClientProtocol):
    """Wrapper around the OpenAI SDK that returns a single-letter answer."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        if OpenAI is None:  # pragma: no cover
            raise RuntimeError("openai package not available")
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)

    def _completion(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=settings.openai_model,
            temperature=settings.temperature,
            input=[
                {"role": "system", "content": settings.openai_system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "quiz_answer",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string",
                                "enum": ["A", "B", "C", "D"],
                            }
                        },
                        "required": ["answer"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        return response.output_text

    def ask(self, question: str, options: List[str], retries: int = 3) -> str:
        """Return the model's single-letter answer with basic retries."""
        opts = "\n".join(
            f"{chr(ord('A') + i)}. {opt}" for i, opt in enumerate(options)
        )
        prompt = f"{question}\n{opts}" if opts else question

        for attempt in range(1, retries + 1):
            try:
                raw = self._completion(prompt)
                data = QuizAnswer.model_validate_json(raw)
                return data.answer
            except TRANSIENT_ERRORS as exc:
                if attempt == retries:
                    raise RuntimeError(f"OpenAI transient error: {exc}") from exc
                time.sleep(2 ** (attempt - 1))
            except ValidationError as exc:
                raise RuntimeError(f"Invalid model response: {exc}") from exc
            except Exception as exc:
                raise RuntimeError(f"Invalid model response: {exc}") from exc
        raise RuntimeError("Failed to get model response")
