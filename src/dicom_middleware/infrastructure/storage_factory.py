"""Factory for storage backend (local or GCS). Cached per backend type."""

from dicom_middleware.config import get_settings
from dicom_middleware.domain.storage import StorageBackend
from dicom_middleware.infrastructure.gcs_storage import GCSStorageBackend
from dicom_middleware.infrastructure.local_storage import LocalStorageBackend

_cached_local: LocalStorageBackend | None = None
_cached_gcs: GCSStorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """
    Return the configured storage backend (local or GCS).
    Backend instance is cached per type; changing STORAGE_BACKEND at runtime requires process restart.
    """
    global _cached_local, _cached_gcs
    settings = get_settings()
    if settings.storage_backend == "gcs":
        if _cached_gcs is None:
            _cached_gcs = GCSStorageBackend()
        return _cached_gcs
    if _cached_local is None:
        _cached_local = LocalStorageBackend()
    return _cached_local
