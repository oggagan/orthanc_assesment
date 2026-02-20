"""Unit tests for domain schemas."""

from datetime import datetime, timezone
from dicom_middleware.domain.entities import StudyMetadata
from dicom_middleware.domain.events import DicomMetadataEvent, DLQPayload


def test_study_metadata_model():
    m = StudyMetadata(study_instance_uid="1.2.3", patient_id="P1", modality="CT", study_date="20250101")
    assert m.study_instance_uid == "1.2.3"
    assert m.patient_id == "P1"
    assert m.modality == "CT"
    assert m.study_date == "20250101"


def test_dicom_metadata_event_to_json_bytes():
    e = DicomMetadataEvent(
        correlation_id="cid-1",
        study_instance_uid="1.2.3",
        patient_id="P1",
        modality="CT",
        study_date="20250101",
        storage_path="file:///data/dicom/studies/1.2.3.dcm",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    raw = e.to_json_bytes()
    assert isinstance(raw, bytes)
    assert b"1.2.3" in raw
    assert b"cid-1" in raw


def test_dlq_payload_to_json_bytes():
    p = DLQPayload(
        original_payload={"orthanc_study_id": "abc"},
        error_reason="Metadata parsing failure",
        correlation_id="cid-1",
    )
    raw = p.to_json_bytes()
    assert isinstance(raw, bytes)
    assert b"Metadata parsing failure" in raw
    assert b"cid-1" in raw
