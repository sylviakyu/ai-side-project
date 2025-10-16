"""FastAPI dependency wiring for TaskFlow API services."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from taskflow_core import Database

from .infra.mq import TaskEventPublisher
from .infra.cache import RedisClient
from .services.tasks import TaskService

database: Database | None = None
publisher: TaskEventPublisher | None = None
redis_client: RedisClient | None = None


async def get_session() -> AsyncSession:
    """Return an async SQLAlchemy session managed by the shared Database helper."""
    if database is None:
        raise RuntimeError("Database dependency not configured.")
    async with database.session() as session:
        yield session


async def get_task_service(
    session: AsyncSession = Depends(get_session),
) -> TaskService:
    """Provide a TaskService instance wired with the current DB session and MQ publisher."""
    return TaskService(session=session, publisher=publisher)


async def redis_client_dependency() -> Redis | None:
    """Expose the Redis client if available; return None when Redis is not configured."""
    if redis_client is None:
        return None
    try:
        return redis_client.client
    except RuntimeError:
        return None
