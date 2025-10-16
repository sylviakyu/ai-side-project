from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow_core import Task, TaskStatus, TaskStatusMessage

logger = logging.getLogger(__name__)


class TaskProcessor:
    """Update task lifecycle state and emit status messages."""

    def __init__(self, redis_publisher, clock=None):
        self._redis = redis_publisher
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    async def _transition(
        self,
        session: AsyncSession,
        task: Task,
        status: TaskStatus,
        *,
        progress: float,
        message: str | None = None,
    ) -> None:
        task.status = status
        task.updated_at = self._clock()
        if status in (TaskStatus.DONE, TaskStatus.FAILED):
            task.finished_at = task.updated_at
        session.add(task)
        await session.commit()
        await session.refresh(task)

        status_message = TaskStatusMessage(
            task_id=task.id,
            status=task.status,
            progress=progress,
            updated_at=task.updated_at,
            message=message,
        )
        try:
            await self._redis.publish(status_message)
        except Exception as exc:  # pragma: no cover - relies on external redis
            logger.warning("Failed to publish Redis message: %s", exc)

    async def _simulate_work(self, payload: Dict[str, Any]) -> None:
        # Placeholder for CPU/IO intensive work - mimic load to illustrate lifecycle.
        await asyncio.sleep(1)

    async def process(self, session: AsyncSession, task_id: str, payload: Dict[str, Any] | None) -> None:
        query = select(Task).where(Task.id == task_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        if task is None:
            logger.warning("Received task %s but it does not exist in the database", task_id)
            return

        if task.status in (TaskStatus.DONE, TaskStatus.FAILED):
            logger.info("Task %s already completed with status %s", task.id, task.status)
            return

        await self._transition(session, task, TaskStatus.PROCESSING, progress=0.1)

        try:
            await self._simulate_work(payload or {})
        except Exception as exc:
            logger.exception("Task %s failed during processing", task.id, exc_info=exc)
            await self._transition(session, task, TaskStatus.FAILED, progress=1.0, message=str(exc))
            return

        await self._transition(session, task, TaskStatus.DONE, progress=1.0)
