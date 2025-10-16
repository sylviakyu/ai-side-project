from __future__ import annotations

from typing import AsyncIterator

from redis.asyncio import Redis


async def stream_task_updates(redis: Redis, task_id: str) -> AsyncIterator[str]:
    """Yield messages from the task-specific Redis channel."""

    channel_name = f"task.status.{task_id}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel_name)
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = message.get("data")
            if data:
                yield data
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
