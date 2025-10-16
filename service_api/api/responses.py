from __future__ import annotations

from typing import Any, Dict


def websocket_error(message: str) -> Dict[str, Any]:
    return {"type": "error", "message": message}
