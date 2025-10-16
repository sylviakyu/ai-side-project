from __future__ import annotations

from typing import Awaitable, Callable, Optional

import aio_pika


class TaskQueueConsumer:
    """Consume task creation messages from RabbitMQ."""

    def __init__(
        self,
        amqp_url: str,
        exchange: str,
        queue_name: str,
        routing_key: str,
    ):
        self._amqp_url = amqp_url
        self._exchange_name = exchange
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._queue: Optional[aio_pika.Queue] = None

    async def connect(self, *, prefetch: int) -> None:
        if self._connection:
            return
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=prefetch)
        exchange = await self._channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        self._queue = await self._channel.declare_queue(
            self._queue_name,
            durable=True,
        )
        await self._queue.bind(exchange, routing_key=self._routing_key)

    async def consume(
        self,
        handler: Callable[[aio_pika.IncomingMessage], Awaitable[None]],
    ) -> None:
        if self._queue is None:
            raise RuntimeError("Queue not initialised.")
        await self._queue.consume(handler, no_ack=False)

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._queue = None
