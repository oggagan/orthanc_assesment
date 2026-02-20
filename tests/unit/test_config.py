"""Unit tests for config validation."""

import pytest

from dicom_middleware.config import Settings


def test_settings_gcs_requires_bucket():
    """When storage_backend is gcs, GCS_BUCKET must be set and non-empty."""
    with pytest.raises(ValueError, match="GCS_BUCKET is required when STORAGE_BACKEND=gcs"):
        Settings(storage_backend="gcs", gcs_bucket=None)
    with pytest.raises(ValueError, match="GCS_BUCKET is required when STORAGE_BACKEND=gcs"):
        Settings(storage_backend="gcs", gcs_bucket="")
    with pytest.raises(ValueError, match="GCS_BUCKET is required when STORAGE_BACKEND=gcs"):
        Settings(storage_backend="gcs", gcs_bucket="   ")


def test_settings_gcs_accepts_non_empty_bucket():
    """When storage_backend is gcs and GCS_BUCKET is set, validation passes."""
    s = Settings(storage_backend="gcs", gcs_bucket="my-bucket")
    assert s.storage_backend == "gcs"
    assert s.gcs_bucket == "my-bucket"
