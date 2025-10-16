"""REST endpoints for task creation and retrieval."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from taskflow_core import TaskCreate, TaskRead

from ..services.tasks import TaskService
from ..dependencies import get_task_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Create a new task row and enqueue it for processing."""
    return await service.create_task(payload)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    """Return all persisted tasks ordered by most recent creation."""
    return await service.list_tasks()


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Fetch a single task by identifier or raise 404 if missing."""
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
