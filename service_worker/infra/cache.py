from __future__ import annotations

import json
from typing import Optional

from redis.asyncio import Redis, from_url

from taskflow_core.schemas import TaskStatusMessage


class RedisPublisher:
    """Publish task status updates via Redis Pub/Sub."""

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._client: Optional[Redis] = None

    async def connect(self) -> Redis:
        if self._client is None:
            self._client = from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def publish(self, message: TaskStatusMessage) -> None:
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        channel = f"task.status.{message.task_id}"
        await self._client.publish(channel, json.dumps(message.dict()))

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        return self._client
