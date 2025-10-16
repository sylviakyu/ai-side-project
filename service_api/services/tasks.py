from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow_core import Task, TaskCreate, TaskRead, TaskStatus, TaskCreatedMessage

from ..infra.mq import TaskEventPublisher

logger = logging.getLogger(__name__)


def _to_schema(task: Task) -> TaskRead:
    return TaskRead(
        task_id=task.id,
        title=task.title,
        payload=task.payload,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        finished_at=task.finished_at,
    )


class TaskService:
    """Coordinate database persistence and outbound events for tasks."""

    def __init__(
        self,
        session: AsyncSession,
        publisher: TaskEventPublisher | None,
    ):
        self._session = session
        self._publisher = publisher

    async def create_task(self, payload: TaskCreate) -> TaskRead:
        task = Task(
            id=str(uuid4()),
            title=payload.title,
            payload=payload.payload,
            status=TaskStatus.PENDING,
        )
        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)

        message = TaskCreatedMessage(
            task_id=task.id,
            payload=payload.payload,
            requested_at=datetime.now(timezone.utc),
        )
        if self._publisher is not None:
            try:
                await self._publisher.publish_task_created(message)
            except Exception as exc:
                logger.exception("Failed to publish task.created event", exc_info=exc)

        return _to_schema(task)

    async def list_tasks(self) -> list[TaskRead]:
        result = await self._session.execute(select(Task).order_by(Task.created_at.desc()))
        tasks = result.scalars().all()
        return [_to_schema(task) for task in tasks]

    async def get_task(self, task_id: str) -> Optional[TaskRead]:
        query = select(Task).where(Task.id == task_id)
        result = await self._session.execute(query)
        task = result.scalar_one_or_none()
        if task is None:
            return None
        return _to_schema(task)
