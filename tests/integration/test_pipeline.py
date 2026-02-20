"""Integration tests for pipeline (mocked Orthanc, DB, Kafka, storage)."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.application.pipeline import run_pipeline
from dicom_middleware.domain.entities import StudyMetadata


@pytest.fixture
def mock_session():
    s = AsyncMock(spec=AsyncSession)
    return s


@pytest.mark.asyncio
async def test_pipeline_send_to_dlq_on_storage_failure(mock_session):
    """When storage fails (e.g. read-only local or GCS error), pipeline sends to DLQ."""
    with (
        patch("dicom_middleware.application.pipeline.OrthancClient") as OrthancCls,
        patch("dicom_middleware.application.pipeline.extract_metadata") as extract,
        patch("dicom_middleware.application.pipeline.upsert_study", new_callable=AsyncMock),
        patch("dicom_middleware.application.pipeline.get_storage_backend") as get_storage_backend,
        patch("dicom_middleware.application.pipeline.send_to_dlq", new_callable=AsyncMock) as send_dlq,
    ):
        orthanc = OrthancCls.return_value
        orthanc.get_first_instance_archive = AsyncMock(return_value=b"dummy-dicom-bytes")
        extract.return_value = StudyMetadata(
            study_instance_uid="1.2.3",
            patient_id="P1",
            modality="CT",
            study_date="20250101",
        )
        mock_storage = MagicMock()
        mock_storage.save.side_effect = OSError("Permission denied")
        get_storage_backend.return_value = mock_storage

        with pytest.raises(OSError):
            await run_pipeline("a1b2c3d4-e5f6-7890-abcd-ef1234567890", "orthanc-study-id", mock_session)

        send_dlq.assert_called_once()
        payload = send_dlq.call_args[0][0]
        assert payload.error_reason == "Storage write failure"
        assert payload.correlation_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
