from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager

from aio_pika import IncomingMessage

from taskflow_core import Database
from taskflow_core.schemas import TaskCreatedMessage

from .core.config import get_settings
from .infra.cache import RedisPublisher
from .infra.db import create_database
from .infra.mq import TaskQueueConsumer
from .services.processor import TaskProcessor


logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan():
    settings = get_settings()

    database = create_database(settings.db_url, echo=settings.db_echo)
    redis = RedisPublisher(settings.redis_url)
    consumer = TaskQueueConsumer(
        settings.rabbitmq_url,
        exchange=settings.rabbitmq_exchange,
        queue_name=settings.rabbitmq_queue,
        routing_key=settings.rabbitmq_routing_key,
    )

    db_attempts = settings.db_connect_attempts
    db_backoff = settings.db_connect_backoff
    for attempt in range(1, db_attempts + 1):
        try:
            await database.create_all()
            break
        except Exception as exc:
            if attempt == db_attempts:
                logger.error("Failed to connect to MySQL after %s attempts", db_attempts)
                raise
            wait_time = db_backoff * attempt
            logger.warning(
                "MySQL unavailable (attempt %s/%s): %s. Retrying in %.1fs",
                attempt,
                db_attempts,
                exc,
                wait_time,
            )
            await asyncio.sleep(wait_time)

    await redis.connect()

    attempts = settings.rabbitmq_connect_attempts
    backoff = settings.rabbitmq_connect_backoff
    for attempt in range(1, attempts + 1):
        try:
            await consumer.connect(prefetch=settings.worker_prefetch)
            break
        except Exception as exc:  # pragma: no cover - integration behaviour
            if attempt == attempts:
                logger.error("Failed to connect to RabbitMQ after %s attempts", attempts)
                raise
            wait_time = backoff * attempt
            logger.warning(
                "RabbitMQ unavailable (attempt %s/%s): %s. Retrying in %.1fs",
                attempt,
                attempts,
                exc,
                wait_time,
            )
            await asyncio.sleep(wait_time)

    try:
        yield database, redis, consumer
    finally:
        await consumer.close()
        await redis.close()
        await database.dispose()


async def handle_message(
    database: Database,
    processor: TaskProcessor,
    message: IncomingMessage,
) -> None:
    async with message.process(ignore_processed=True):
        try:
            payload = json.loads(message.body)
            event = TaskCreatedMessage(**payload)
        except Exception as exc:
            logger.exception("Invalid task.created payload", exc_info=exc)
            return

        async with database.session() as session:
            await processor.process(session, event.task_id, event.payload)


async def run_worker() -> None:
    async with app_lifespan() as (database, redis, consumer):
        processor = TaskProcessor(redis)

        await consumer.consume(lambda message: handle_message(database, processor, message))

        stop_event = asyncio.Event()
        await stop_event.wait()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker shutdown requested")


if __name__ == "__main__":
    main()
