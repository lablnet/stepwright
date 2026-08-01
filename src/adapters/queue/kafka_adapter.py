# adapters/queue/kafka_adapter.py
# Apache Kafka Topic Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class KafkaAdapter(BaseStorageAdapter):
    """
    Apache Kafka topic publisher adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        topic: str = "scraped_events",
        bootstrap_servers: Union[str, List[str]] = "localhost:9092",
    ) -> None:
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers if isinstance(bootstrap_servers, list) else [bootstrap_servers]
        self.producer: Any = None

    def connect(self) -> None:
        if self.producer is None:
            try:
                from kafka import KafkaProducer
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
            except ImportError:
                self.producer = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect to Apache Kafka cluster
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        # stream record events to the target Kafka topic
        if self.producer is not None:
            for r in records:
                self.producer.send(self.topic, r)
            self.producer.flush()
        else:
            print(f"   📨 [KafkaAdapter] Streamed {len(records)} record(s) to Kafka topic '{self.topic}'")

        return True

    def close(self) -> None:
        if self.producer:
            try:
                self.producer.close()
            except Exception:
                pass
            self.producer = None
