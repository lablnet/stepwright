# adapters/queue/rabbitmq_adapter.py
# RabbitMQ / AMQP Message Queue Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class RabbitMQAdapter(BaseStorageAdapter):
    """
    RabbitMQ / AMQP message queue publisher adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        queue_name: str = "scraped_data_queue",
        host: str = "localhost",
        port: int = 5672,
    ) -> None:
        self.queue_name = queue_name
        self.host = host
        self.port = port
        self.connection: Any = None
        self.channel: Any = None

    def connect(self) -> None:
        if self.connection is None:
            try:
                import pika
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
            except ImportError:
                self.connection = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect to RabbitMQ broker
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        if self.channel is not None:
            try:
                import pika
                props = pika.BasicProperties(delivery_mode=2)
            except ImportError:
                props = None

            # publish each JSON-serialized record to the RabbitMQ queue
            for r in records:
                payload = json.dumps(r)
                self.channel.basic_publish(
                    exchange="",
                    routing_key=self.queue_name,
                    body=payload,
                    properties=props,
                )
        else:
            print(f"   🐰 [RabbitMQAdapter] Published {len(records)} record(s) to queue '{self.queue_name}' ({self.host}:{self.port})")

        return True

    def close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
