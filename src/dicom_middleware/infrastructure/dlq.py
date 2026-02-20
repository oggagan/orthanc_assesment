"""Dead letter queue: publish to dicom.metadata.dlq on failure."""

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from dicom_middleware.config import get_settings
from dicom_middleware.domain.events import DLQPayload
from dicom_middleware.observability.logging import get_logger
from dicom_middleware.observability.metrics import DLQ_MESSAGES

_log = get_logger(__name__)

_dlq_producer: AIOKafkaProducer | None = None


async def get_dlq_producer() -> AIOKafkaProducer:
    global _dlq_producer
    if _dlq_producer is None:
        settings = get_settings()
        _dlq_producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            enable_idempotence=True,
            acks="all",
        )
        await _dlq_producer.start()
    return _dlq_producer


async def close_dlq_producer() -> None:
    global _dlq_producer
    if _dlq_producer is not None:
        await _dlq_producer.stop()
        _dlq_producer = None


async def send_to_dlq(payload: DLQPayload, reason: str) -> None:
    """Publish payload to dicom.metadata.dlq and record metric."""
    try:
        producer = await get_dlq_producer()
        settings = get_settings()
        await producer.send_and_wait(
            settings.kafka_dlq_topic,
            value=payload.to_json_bytes(),
        )
        DLQ_MESSAGES.labels(reason=payload.error_reason).inc()
        _log.info("dlq_sent", reason=payload.error_reason, correlation_id=payload.correlation_id)
    except Exception as e:
        _log.exception("dlq_send_failed", error=str(e), correlation_id=payload.correlation_id)
        raise
