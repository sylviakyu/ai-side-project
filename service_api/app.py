from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

import logging

from taskflow_core import Database

from .api.routes_tasks import router as tasks_router
from .api.routes_ws import router as ws_router
from .core.config import get_settings
from .infra.cache import RedisClient
from .infra.mq import TaskEventPublisher


logger = logging.getLogger(__name__)


def create_app(*, with_infra: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from . import dependencies

        if with_infra:
            dependencies.database = Database(settings.db_url, echo=settings.db_echo)
            dependencies.publisher = TaskEventPublisher(
                settings.rabbitmq_url,
                exchange_name=settings.rabbitmq_exchange,
                routing_key=settings.rabbitmq_routing_key,
            )
            dependencies.redis_client = RedisClient(settings.redis_url)

            db_attempts = settings.db_connect_attempts
            db_backoff = settings.db_connect_backoff
            for attempt in range(1, db_attempts + 1):
                try:
                    await dependencies.database.create_all()
                    break
                except Exception as exc:  # pragma: no cover - exercised in integration setups
                    if attempt == db_attempts:
                        logger.warning("Database initialisation failed: %s", exc)
                        raise
                    wait_time = db_backoff * attempt
                    logger.warning(
                        "Database unavailable (attempt %s/%s): %s. Retrying in %.1fs",
                        attempt,
                        db_attempts,
                        exc,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)

            try:
                await dependencies.publisher.connect()
            except Exception as exc:  # pragma: no cover - exercised in integration setups
                logger.warning("RabbitMQ connection failed: %s", exc)
                dependencies.publisher = None

            try:
                await dependencies.redis_client.connect()
            except Exception as exc:  # pragma: no cover - exercised in integration setups
                logger.warning("Redis connection failed: %s", exc)
                dependencies.redis_client = None

            try:
                yield
            finally:
                if dependencies.publisher is not None:
                    await dependencies.publisher.close()
                if dependencies.redis_client is not None:
                    await dependencies.redis_client.close()
                if dependencies.database is not None:
                    await dependencies.database.dispose()
        else:
            yield

    app = FastAPI(title="TaskFlow API", lifespan=lifespan)

    @app.get("/healthz")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(tasks_router)
    app.include_router(ws_router)
    return app


app = create_app()
