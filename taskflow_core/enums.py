"""Enumerations shared across TaskFlow services."""

from enum import Enum


class TaskStatus(str, Enum):
    """Shared task lifecycle states."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"
