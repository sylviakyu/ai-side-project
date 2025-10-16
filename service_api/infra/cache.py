"""Redis client management for the API service."""

from __future__ import annotations

from typing import Optional

from redis.asyncio import Redis, from_url


class RedisClient:
    """Lazy Redis connection manager."""

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._client: Optional[Redis] = None

    async def connect(self) -> Redis:
        """Lazily allocate and cache a Redis client."""
        if self._client is None:
            self._client = from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the cached Redis connection if present."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> Redis:
        """Return the connected client or raise if not initialised."""
        if self._client is None:
            raise RuntimeError("Redis client has not been initialised.")
        return self._client
