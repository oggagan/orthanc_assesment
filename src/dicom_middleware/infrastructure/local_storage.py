"""Local filesystem storage for raw DICOM. Path: {STORAGE_PATH}/studies/{StudyInstanceUID}.dcm"""

import time
from pathlib import Path

from dicom_middleware.config import get_settings
from dicom_middleware.observability.metrics import (
    STORAGE_UPLOAD_DURATION_SECONDS,
    STORAGE_UPLOAD_TOTAL,
)


class LocalStorageBackend:
    """Store raw DICOM on local disk; implements StorageBackend protocol."""

    def save(self, study_instance_uid: str, data: bytes) -> str:
        """
        Write DICOM bytes to {STORAGE_PATH}/studies/{StudyInstanceUID}.dcm.
        Creates parent directories if needed. Overwrites if file exists (idempotent).
        Returns the storage path as file URI, e.g. file:///data/dicom/studies/1.2.3.dcm.
        """
        start = time.perf_counter()
        try:
            uri = save_dicom(study_instance_uid, data)
            STORAGE_UPLOAD_DURATION_SECONDS.labels(backend="local").observe(
                time.perf_counter() - start
            )
            STORAGE_UPLOAD_TOTAL.labels(backend="local", status="success").inc()
            return uri
        except Exception:
            STORAGE_UPLOAD_DURATION_SECONDS.labels(backend="local").observe(
                time.perf_counter() - start
            )
            STORAGE_UPLOAD_TOTAL.labels(backend="local", status="failure").inc()
            raise


def save_dicom(study_instance_uid: str, data: bytes) -> str:
    """
    Write DICOM bytes to {STORAGE_PATH}/studies/{StudyInstanceUID}.dcm.
    Creates parent directories if needed. Overwrites if file exists (idempotent).
    Returns the storage path as file URI, e.g. file:///data/dicom/studies/1.2.3.dcm.
    """
    settings = get_settings()
    base = Path(settings.storage_path)
    studies_dir = base / "studies"
    studies_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize UID for filename (replace path separators if any)
    safe_uid = study_instance_uid.replace("/", "_").replace("\\", "_")
    file_path = studies_dir / f"{safe_uid}.dcm"
    file_path.write_bytes(data)
    return file_path.as_uri()
