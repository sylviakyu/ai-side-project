"""Pydantic schemas shared between the API and worker services."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import TaskStatus


class TaskCreate(BaseModel):
    """Payload accepted by the API when creating a new task."""

    title: str = Field(..., max_length=255)
    payload: Optional[dict[str, Any]] = None


class TaskRead(BaseModel):
    """Representation returned by the API and used across services."""

    task_id: str
    title: str
    payload: Optional[dict[str, Any]] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class TaskCreatedMessage(BaseModel):
    """Message published to RabbitMQ when a task is created."""

    task_id: str
    payload: Optional[dict[str, Any]] = None
    requested_at: datetime


class TaskStatusMessage(BaseModel):
    """Message propagated over Redis Pub/Sub when a task changes state."""

    task_id: str
    status: TaskStatus
    progress: float = 0.0
    updated_at: datetime
    message: Optional[str] = None

    class Config:
        use_enum_values = True
