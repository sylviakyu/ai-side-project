"""RabbitMQ publisher utilities for the API service."""

from __future__ import annotations

from typing import Optional

import aio_pika

from taskflow_core.schemas import TaskCreatedMessage


class TaskEventPublisher:
    """Publish task events to RabbitMQ."""

    def __init__(
        self,
        amqp_url: str,
        exchange_name: str = "task.topic",
        routing_key: str = "task.created",
    ):
        self._amqp_url = amqp_url
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._exchange: Optional[aio_pika.Exchange] = None

    async def connect(self) -> None:
        """Establish a connection and declare the exchange if needed."""
        if self._connection:
            return
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

    async def close(self) -> None:
        """Gracefully close the AMQP connection."""
        if self._connection:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None

    async def publish_task_created(self, message: TaskCreatedMessage) -> None:
        """Send a `task.created` message to the configured exchange."""
        if self._connection is None or self._channel is None or self._exchange is None:
            await self.connect()

        body = message.json().encode("utf-8")
        await self._exchange.publish(
            aio_pika.Message(body=body),
            routing_key=self._routing_key,
        )
