"""Google Cloud Storage backend for raw DICOM. Object path: gs://{bucket}/studies/{StudyInstanceUID}.dcm"""

import time
from typing import TYPE_CHECKING

from dicom_middleware.config import get_settings
from dicom_middleware.observability.logging import get_logger
from dicom_middleware.observability.metrics import (
    STORAGE_UPLOAD_DURATION_SECONDS,
    STORAGE_UPLOAD_TOTAL,
)

if TYPE_CHECKING:
    from google.cloud.storage import Client
    from google.cloud.storage.bucket import Bucket

_log = get_logger(__name__)


class GCSStorageBackend:
    """
    Store raw DICOM in GCS; implements StorageBackend protocol.
    Uses GOOGLE_APPLICATION_CREDENTIALS for auth. Client is created in __init__ and reused.
    """

    def __init__(self) -> None:
        self._client: "Client | None" = None

    def _get_client(self) -> "Client":
        if self._client is None:
            from google.cloud import storage

            settings = get_settings()
            self._client = storage.Client(project=settings.gcs_project)
        return self._client

    def save(self, study_instance_uid: str, data: bytes) -> str:
        """
        Upload DICOM bytes to gs://{bucket}/studies/{safe_uid}.dcm.
        Returns the gs:// URI. Raises on GCS errors (pipeline will send to DLQ).
        """
        settings = get_settings()
        bucket_name = settings.gcs_bucket
        if not bucket_name or not bucket_name.strip():
            raise ValueError("GCS_BUCKET is required when using GCS storage backend")
        timeout = settings.gcs_upload_timeout_seconds
        start = time.perf_counter()
        safe_uid = study_instance_uid.replace("/", "_").replace("\\", "_")
        blob_name = f"studies/{safe_uid}.dcm"
        try:
            client = self._get_client()
            bucket: Bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.metadata = {"study_instance_uid": study_instance_uid}
            blob.upload_from_string(
                data,
                content_type="application/dicom",
                timeout=timeout,
            )
            uri = f"gs://{bucket_name}/{blob_name}"
            STORAGE_UPLOAD_DURATION_SECONDS.labels(backend="gcs").observe(
                time.perf_counter() - start
            )
            STORAGE_UPLOAD_TOTAL.labels(backend="gcs", status="success").inc()
            _log.info(
                "gcs_upload_success",
                study_instance_uid=study_instance_uid,
                gcs_uri=uri,
                size_bytes=len(data),
            )
            return uri
        except Exception as e:
            STORAGE_UPLOAD_DURATION_SECONDS.labels(backend="gcs").observe(
                time.perf_counter() - start
            )
            STORAGE_UPLOAD_TOTAL.labels(backend="gcs", status="failure").inc()
            error_type = type(e).__name__
            _log.warning(
                "gcs_upload_failed",
                study_instance_uid=study_instance_uid,
                error_type=error_type,
            )
            # Do not expose GCS/credential details to pipeline or logs
            raise RuntimeError("GCS upload failed") from e
