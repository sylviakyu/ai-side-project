"""Response helpers for WebSocket messaging."""

from __future__ import annotations

from typing import Any, Dict


def websocket_error(message: str) -> Dict[str, Any]:
    """Render an error payload that can be sent over a WebSocket connection."""
    return {"type": "error", "message": message}
