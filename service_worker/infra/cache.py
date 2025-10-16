"""Redis publishing helpers for broadcasting worker status updates."""

from __future__ import annotations

import json
from typing import Optional

from redis.asyncio import Redis, from_url

from taskflow_core.schemas import TaskStatusMessage


BROADCAST_CHANNEL = "task.status"


class RedisPublisher:
    """Publish task status updates via Redis Pub/Sub."""

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._client: Optional[Redis] = None

    async def connect(self) -> Redis:
        """Create and cache an asyncio Redis client if missing."""
        if self._client is None:
            self._client = from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the Redis connection and clear the cached client."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def publish(self, message: TaskStatusMessage) -> None:
        """Publish a TaskStatusMessage on the broadcast channel."""
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        await self._client.publish(BROADCAST_CHANNEL, message.json())

    async def publish_status_update(self, task_id: str, payload: dict) -> None:
        """Publish an ad-hoc status payload on the broadcast channel."""
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        await self._client.publish(BROADCAST_CHANNEL, json.dumps(payload))

    @property
    def client(self) -> Redis:
        """Return the live Redis client or raise if it is disconnected."""
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        return self._client
