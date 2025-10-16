from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from taskflow_core import TaskCreate, TaskRead, TaskStatus

from service_api.app import create_app
from service_api.dependencies import get_task_service


class InMemoryTaskService:
    """Lightweight stand-in for the TaskService during unit tests."""

    def __init__(self):
        self._tasks: Dict[str, TaskRead] = {}

    async def create_task(self, payload: TaskCreate) -> TaskRead:
        task_id = str(uuid4())
        timestamp = datetime.now(timezone.utc)
        task = TaskRead(
            task_id=task_id,
            title=payload.title,
            payload=payload.payload,
            status=TaskStatus.PENDING,
            created_at=timestamp,
            updated_at=timestamp,
            finished_at=None,
        )
        self._tasks[task_id] = task
        return task

    async def get_task(self, task_id: str) -> Optional[TaskRead]:
        return self._tasks.get(task_id)


@pytest.fixture()
def client():
    app = create_app(with_infra=False)
    service = InMemoryTaskService()

    async def override_service() -> InMemoryTaskService:
        return service

    app.dependency_overrides[get_task_service] = override_service

    with TestClient(app) as test_client:
        yield test_client


def test_create_task_returns_pending_status(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Example Task", "payload": {"value": 42}},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == TaskStatus.PENDING.value
    assert body["title"] == "Example Task"
    assert "task_id" in body


def test_get_task_returns_created_task(client: TestClient):
    post_response = client.post("/tasks", json={"title": "Fetch Task"})
    task_id = post_response.json()["task_id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["task_id"] == task_id
    assert payload["status"] == TaskStatus.PENDING.value
