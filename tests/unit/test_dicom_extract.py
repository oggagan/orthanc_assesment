"""Unit tests for DICOM metadata extraction."""

import io
import pytest
from pydicom import Dataset, dcmwrite

from dicom_middleware.domain.entities import StudyMetadata
from dicom_middleware.infrastructure.dicom_extract import extract_metadata


def _make_minimal_dicom(study_uid: str, patient_id: str | None = None, modality: str | None = None, study_date: str | None = None) -> bytes:
    """Create minimal DICOM bytes with required and optional tags."""
    ds = Dataset()
    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = "1.2.3.4.5"
    ds.SOPInstanceUID = "1.2.3.4.5.6"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
    if patient_id is not None:
        ds.PatientID = patient_id
    if modality is not None:
        ds.Modality = modality
    if study_date is not None:
        ds.StudyDate = study_date
    buf = io.BytesIO()
    dcmwrite(buf, ds, implicit_vr=True, little_endian=True)
    return buf.getvalue()


def test_extract_metadata_minimal():
    data = _make_minimal_dicom("1.2.3.4")
    meta = extract_metadata(data)
    assert meta.study_instance_uid == "1.2.3.4"
    assert meta.patient_id is None
    assert meta.modality is None
    assert meta.study_date is None


def test_extract_metadata_all_fields():
    data = _make_minimal_dicom("1.2.3", patient_id="P001", modality="CT", study_date="20250101")
    meta = extract_metadata(data)
    assert meta.study_instance_uid == "1.2.3"
    assert meta.patient_id == "P001"
    assert meta.modality == "CT"
    assert meta.study_date == "20250101"


def test_extract_metadata_invalid_dicom_raises():
    with pytest.raises(ValueError):
        extract_metadata(b"not dicom")


def test_extract_metadata_missing_study_instance_uid_raises():
    ds = Dataset()
    ds.SeriesInstanceUID = "1.2.3"
    ds.SOPInstanceUID = "1.2.3.4"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
    buf = io.BytesIO()
    dcmwrite(buf, ds, implicit_vr=True, little_endian=True)
    with pytest.raises(ValueError, match="Missing StudyInstanceUID"):
        extract_metadata(buf.getvalue())
