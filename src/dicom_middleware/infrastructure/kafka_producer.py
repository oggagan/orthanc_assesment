"""Kafka producer: idempotent, acks=all, topic dicom.metadata.v1; correlation_id in headers."""

from datetime import datetime, timezone
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from dicom_middleware.config import get_settings
from dicom_middleware.domain.events import DicomMetadataEvent

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        settings = get_settings()
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            enable_idempotence=True,
            acks="all",
        )
        await _producer.start()
    return _producer


async def close_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def publish_metadata_event(event: DicomMetadataEvent) -> None:
    """Send event to dicom.metadata.v1 with correlation_id in headers."""
    producer = await get_producer()
    settings = get_settings()
    await producer.send_and_wait(
        settings.kafka_topic,
        value=event.to_json_bytes(),
        headers=[("correlation_id", event.correlation_id.encode("utf-8"))],
    )
