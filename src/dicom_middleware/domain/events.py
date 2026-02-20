"""Kafka event and DLQ payload schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DicomMetadataEvent(BaseModel):
    """Event published to dicom.metadata.v1."""

    correlation_id: str = Field(description="Request correlation ID for tracing")
    study_instance_uid: str = Field(description="DICOM Study Instance UID")
    patient_id: str | None = Field(default=None, description="Patient ID")
    modality: str | None = Field(default=None, description="Modality")
    study_date: str | None = Field(default=None, description="Study Date")
    storage_path: str = Field(description="Path or URI to raw DICOM (e.g. file:///data/dicom/studies/...)")
    timestamp: str = Field(description="ISO 8601 timestamp when event was created")

    def to_json_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")


class DLQPayload(BaseModel):
    """Payload sent to dicom.metadata.dlq on failure."""

    original_payload: dict[str, Any] = Field(description="Original request or context payload")
    error_reason: str = Field(description="Reason for failure (e.g. Metadata parsing failure)")
    correlation_id: str = Field(description="Correlation ID for tracing")

    def to_json_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")
