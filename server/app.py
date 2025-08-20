from __future__ import annotations

import base64
import os
from io import BytesIO
from typing import List, Optional

from celery import Celery
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from quiz_automation.model_client import LocalModelClient
from quiz_automation.ocr import get_backend

# Celery configuration -----------------------------------------------------

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

celery_app = Celery(
    "quiz_tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND
)

# FastAPI application ------------------------------------------------------

app = FastAPI()


class AnswerRequest(BaseModel):
    """Payload for the answer endpoint."""

    question: Optional[str] = None
    image: Optional[str] = None  # Base64 encoded image
    options: List[str]


@celery_app.task
def process_answer(
    question: str | None, image_b64: str | None, options: List[str]
) -> str:
    """Run OCR and model prediction for *question* or *image*."""

    question_text = question or ""
    if image_b64 and not question:
        try:
            from PIL import Image  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Pillow not available") from exc
        img_bytes = base64.b64decode(image_b64)
        with Image.open(BytesIO(img_bytes)) as img:
            ocr_backend = get_backend()
            question_text = ocr_backend(img)

    client = LocalModelClient()
    return client.ask(question_text, options)


@app.post("/answer")
def create_answer(request: AnswerRequest) -> dict[str, str]:
    """Enqueue an OCR/model job and return the task id."""

    task = process_answer.delay(request.question, request.image, request.options)
    return {"task_id": task.id}


@app.get("/answer/{task_id}")
def get_answer(task_id: str) -> dict[str, str]:
    """Return task status and result when available."""

    result = celery_app.AsyncResult(task_id)
    if result.successful():
        return {"status": "completed", "answer": result.result}
    if result.failed():  # pragma: no cover - exercised via tests
        raise HTTPException(status_code=500, detail=str(result.result))
    return {"status": "pending"}
