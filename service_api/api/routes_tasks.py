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
    return await service.create_task(payload)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
