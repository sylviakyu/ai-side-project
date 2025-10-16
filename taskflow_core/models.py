"""SQLAlchemy ORM models representing the TaskFlow persistence layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .enums import TaskStatus


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""


class Task(Base):
    """Task row representing the current processing state."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SqlEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
