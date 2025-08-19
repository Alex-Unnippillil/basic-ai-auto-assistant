from __future__ import annotations

from fastapi.testclient import TestClient

from server.app import app, celery_app


def test_answer_endpoint_eager(monkeypatch) -> None:
    """POST /answer triggers Celery task and returns model response."""

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_store_eager_result = True
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache+memory://"
    client = TestClient(app)

    payload = {
        "question": "What color is the clear sky?",
        "options": ["Blue", "Red", "Green", "Yellow"],
    }
    resp = client.post("/answer", json=payload)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    res = client.get(f"/answer/{task_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["answer"] == "A"
