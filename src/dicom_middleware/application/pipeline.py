"""Pipeline: extract -> DB -> local storage -> Kafka; on failure -> DLQ."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.domain.entities import StudyMetadata
from dicom_middleware.domain.events import DicomMetadataEvent, DLQPayload
from dicom_middleware.infrastructure.dicom_extract import extract_metadata
from dicom_middleware.infrastructure.dlq import send_to_dlq
from dicom_middleware.infrastructure.kafka_producer import publish_metadata_event
from dicom_middleware.infrastructure.orthanc import OrthancClient
from dicom_middleware.infrastructure.storage_factory import get_storage_backend
from dicom_middleware.infrastructure.repository import upsert_study
from dicom_middleware.observability.logging import get_logger
from dicom_middleware.observability.metrics import PIPELINE_FAILURE, PIPELINE_SUCCESS

_log = get_logger(__name__)

DLQ_REASON_METADATA = "Metadata parsing failure"
DLQ_REASON_DB = "DB write failure"
DLQ_REASON_STORAGE = "Storage write failure"
DLQ_REASON_KAFKA = "Kafka publish failure"
DLQ_REASON_VALIDATION = "Schema validation failure"


async def run_pipeline(
    correlation_id: str,
    orthanc_study_id: str,
    session: AsyncSession,
) -> None:
    """
    Run the full pipeline for one study. On any failure, send to DLQ and re-raise or return.
    Idempotent: duplicate study_instance_uid results in upsert and single Kafka message.
    """
    original_payload = {"orthanc_study_id": orthanc_study_id}
    cid_uuid = UUID(correlation_id) if isinstance(correlation_id, str) else correlation_id

    try:
        # 1. Fetch DICOM from Orthanc (first instance)
        client = OrthancClient()
        try:
            dicom_bytes = await client.get_first_instance_archive(orthanc_study_id)
        except Exception as e:
            await send_to_dlq(
                DLQPayload(
                    original_payload=original_payload,
                    error_reason=DLQ_REASON_METADATA,
                    correlation_id=correlation_id,
                ),
                reason=DLQ_REASON_METADATA,
            )
            PIPELINE_FAILURE.labels(reason=DLQ_REASON_METADATA).inc()
            _log.warning("orthanc_fetch_failed", error=str(e), correlation_id=correlation_id)
            raise

        # 2. Extract metadata
        try:
            metadata = extract_metadata(dicom_bytes)
        except ValueError as e:
            await send_to_dlq(
                DLQPayload(
                    original_payload=original_payload,
                    error_reason=DLQ_REASON_METADATA,
                    correlation_id=correlation_id,
                ),
                reason=DLQ_REASON_METADATA,
            )
            PIPELINE_FAILURE.labels(reason=DLQ_REASON_METADATA).inc()
            _log.warning("metadata_extract_failed", error=str(e), correlation_id=correlation_id)
            raise

        # 3. Persist to DB (idempotent upsert)
        try:
            await upsert_study(session, cid_uuid, metadata)
        except Exception as e:
            await send_to_dlq(
                DLQPayload(
                    original_payload=original_payload,
                    error_reason=DLQ_REASON_DB,
                    correlation_id=correlation_id,
                ),
                reason=DLQ_REASON_DB,
            )
            PIPELINE_FAILURE.labels(reason=DLQ_REASON_DB).inc()
            _log.exception("db_write_failed", correlation_id=correlation_id)
            raise

        # 4. Save raw DICOM (local or GCS via factory)
        try:
            storage = get_storage_backend()
            storage_path = storage.save(metadata.study_instance_uid, dicom_bytes)
        except Exception as e:
            await send_to_dlq(
                DLQPayload(
                    original_payload=original_payload,
                    error_reason=DLQ_REASON_STORAGE,
                    correlation_id=correlation_id,
                ),
                reason=DLQ_REASON_STORAGE,
            )
            PIPELINE_FAILURE.labels(reason=DLQ_REASON_STORAGE).inc()
            _log.exception("storage_write_failed", correlation_id=correlation_id)
            raise

        # 5. Publish to Kafka
        event = DicomMetadataEvent(
            correlation_id=correlation_id,
            study_instance_uid=metadata.study_instance_uid,
            patient_id=metadata.patient_id,
            modality=metadata.modality,
            study_date=metadata.study_date,
            storage_path=storage_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        try:
            await publish_metadata_event(event)
        except Exception as e:
            await send_to_dlq(
                DLQPayload(
                    original_payload=original_payload,
                    error_reason=DLQ_REASON_KAFKA,
                    correlation_id=correlation_id,
                ),
                reason=DLQ_REASON_KAFKA,
            )
            PIPELINE_FAILURE.labels(reason=DLQ_REASON_KAFKA).inc()
            _log.exception("kafka_publish_failed", correlation_id=correlation_id)
            raise

        PIPELINE_SUCCESS.inc()
        _log.info(
            "pipeline_success",
            study_instance_uid=metadata.study_instance_uid,
            correlation_id=correlation_id,
        )
    except (ValueError, Exception):
        # Already sent to DLQ and incremented metric where applicable; re-raise for HTTP layer
        raise
