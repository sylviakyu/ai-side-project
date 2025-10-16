from __future__ import annotations

import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from .responses import websocket_error
from ..infra.pubsub import stream_task_updates
from ..dependencies import redis_client_dependency


router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    redis: Redis | None = Depends(redis_client_dependency),
) -> None:
    if redis is None:
        await websocket.accept()
        await websocket.send_text(json.dumps(websocket_error("Realtime updates unavailable")))
        await websocket.close()
        return

    await websocket.accept()
    try:
        async for payload in stream_task_updates(redis):
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        return
