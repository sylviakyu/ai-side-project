from __future__ import annotations

from typing import AsyncIterator

from redis.asyncio import Redis


BROADCAST_CHANNEL = "task.status"


async def stream_task_updates(redis: Redis) -> AsyncIterator[str]:
    """Yield messages for all task status updates from Redis."""

    pubsub = redis.pubsub()
    await pubsub.subscribe(BROADCAST_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = message.get("data")
            if data:
                yield data
    finally:
        await pubsub.unsubscribe(BROADCAST_CHANNEL)
        await pubsub.close()
