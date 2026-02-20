"""Abstract storage interface for raw DICOM. Implementations: LocalStorageBackend (GCS later)."""

from typing import Protocol


class StorageBackend(Protocol):
    """Store DICOM bytes under Study Instance UID; return path/URI for the event."""

    def save(self, study_instance_uid: str, data: bytes) -> str:
        """Write DICOM bytes and return a stable path or URI (e.g. file://... or gs://...)."""
        ...
