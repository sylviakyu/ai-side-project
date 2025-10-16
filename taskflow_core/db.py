"""Async SQLAlchemy database helper utilities."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base


class Database:
    """Async database helper wrapping SQLAlchemy session lifecycle."""

    def __init__(self, url: str, echo: bool = False):
        self._engine = create_async_engine(url, echo=echo, future=True)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async DB session."""
        async with self._session_factory() as session:
            yield session

    async def create_all(self) -> None:
        """Create tables if they do not exist."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """Close the engine and release pooled connections."""
        await self._engine.dispose()
