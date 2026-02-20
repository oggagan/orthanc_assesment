"""Extract DICOM metadata (strict scope: StudyInstanceUID, PatientID, Modality, StudyDate)."""

import io
from pydicom import dcmread
from pydicom.errors import InvalidDicomError

from dicom_middleware.domain.entities import StudyMetadata


def extract_metadata(dicom_bytes: bytes) -> StudyMetadata:
    """
    Parse DICOM and extract only the four required fields.
    Raises ValueError on parse error or missing required StudyInstanceUID.
    """
    try:
        ds = dcmread(io.BytesIO(dicom_bytes), force=True)
    except InvalidDicomError as e:
        raise ValueError(f"Invalid DICOM: {e}") from e

    study_instance_uid = getattr(ds, "StudyInstanceUID", None)
    if not study_instance_uid:
        raise ValueError("Missing StudyInstanceUID")

    return StudyMetadata(
        study_instance_uid=str(study_instance_uid),
        patient_id=getattr(ds, "PatientID", None) and str(ds.PatientID) or None,
        modality=getattr(ds, "Modality", None) and str(ds.Modality) or None,
        study_date=getattr(ds, "StudyDate", None) and str(ds.StudyDate) or None,
    )
