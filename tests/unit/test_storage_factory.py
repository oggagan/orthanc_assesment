"""Unit tests for storage backend factory."""

from unittest.mock import patch

import dicom_middleware.infrastructure.storage_factory as storage_factory
from dicom_middleware.infrastructure.gcs_storage import GCSStorageBackend
from dicom_middleware.infrastructure.local_storage import LocalStorageBackend
from dicom_middleware.infrastructure.storage_factory import get_storage_backend


def _clear_factory_cache():
    storage_factory._cached_local = None
    storage_factory._cached_gcs = None


def test_get_storage_backend_returns_local_when_config_local():
    """When storage_backend is local, factory returns LocalStorageBackend."""
    _clear_factory_cache()
    with patch("dicom_middleware.infrastructure.storage_factory.get_settings") as get_settings:
        settings = type("Settings", (), {"storage_backend": "local"})()
        get_settings.return_value = settings
        backend = get_storage_backend()
    assert isinstance(backend, LocalStorageBackend)


def test_get_storage_backend_returns_gcs_when_config_gcs():
    """When storage_backend is gcs, factory returns GCSStorageBackend."""
    _clear_factory_cache()
    with patch("dicom_middleware.infrastructure.storage_factory.get_settings") as get_settings:
        settings = type("Settings", (), {"storage_backend": "gcs"})()
        get_settings.return_value = settings
        backend = get_storage_backend()
    assert isinstance(backend, GCSStorageBackend)
