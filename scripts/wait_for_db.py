#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


DB_URL = os.getenv("DB_URL", "mysql+asyncmy://user:pass@mysql:3306/taskflow")
MAX_ATTEMPTS = int(os.getenv("DB_CONNECT_ATTEMPTS", "10"))
BACKOFF = float(os.getenv("DB_CONNECT_BACKOFF", "2.0"))


async def check_connection() -> None:
    engine = create_async_engine(DB_URL, echo=False)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    finally:
        await engine.dispose()


async def main() -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            await check_connection()
            print("Database reachable.", flush=True)
            return
        except Exception as exc:
            if attempt == MAX_ATTEMPTS:
                print(f"Database connection failed after {MAX_ATTEMPTS} attempts: {exc}", file=sys.stderr)
                raise

            wait_time = BACKOFF * attempt
            print(
                f"Database unavailable (attempt {attempt}/{MAX_ATTEMPTS}): {exc}. Retrying in {wait_time:.1f}s",
                flush=True,
            )
            await asyncio.sleep(wait_time)


if __name__ == "__main__":
    asyncio.run(main())
