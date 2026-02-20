"""Domain entities and value objects."""

from pydantic import BaseModel, Field


class StudyMetadata(BaseModel):
    """Extracted DICOM metadata (strict scope: 4 fields only)."""

    study_instance_uid: str = Field(description="DICOM Study Instance UID")
    patient_id: str | None = Field(default=None, description="DICOM Patient ID")
    modality: str | None = Field(default=None, description="DICOM Modality (e.g. CT, MR)")
    study_date: str | None = Field(default=None, description="DICOM Study Date")
