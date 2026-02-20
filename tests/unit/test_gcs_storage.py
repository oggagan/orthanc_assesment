"""Unit tests for GCS storage backend (mocked client)."""

import pytest
from unittest.mock import MagicMock, patch


def test_gcs_save_returns_gs_uri():
    """save() uploads to GCS and returns gs://{bucket}/studies/{uid}.dcm."""
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.name = "my-bucket"
    mock_bucket.blob.return_value = mock_blob
    mock_client = MagicMock()
    mock_client.bucket.return_value = mock_bucket

    with patch("dicom_middleware.infrastructure.gcs_storage.get_settings") as get_settings:
        settings = MagicMock()
        settings.gcs_bucket = "my-bucket"
        settings.gcs_upload_timeout_seconds = 60
        get_settings.return_value = settings

        from dicom_middleware.infrastructure.gcs_storage import GCSStorageBackend

        backend = GCSStorageBackend()
        backend._client = mock_client
        uri = backend.save("1.2.3.4", b"dicom-bytes")

    assert uri == "gs://my-bucket/studies/1.2.3.4.dcm"
    mock_bucket.blob.assert_called_once_with("studies/1.2.3.4.dcm")
    mock_blob.upload_from_string.assert_called_once()
    call_args, call_kw = mock_blob.upload_from_string.call_args
    # Positional args: (data,) from our call blob.upload_from_string(data, content_type=..., timeout=...)
    assert b"dicom-bytes" in call_args[0]
    assert call_kw.get("content_type") == "application/dicom"
    assert call_kw.get("timeout") == 60


def test_gcs_save_sanitizes_uid():
    """UID with slashes is sanitized in blob name."""
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.name = "my-bucket"
    mock_bucket.blob.return_value = mock_blob
    mock_client = MagicMock()
    mock_client.bucket.return_value = mock_bucket

    with patch("dicom_middleware.infrastructure.gcs_storage.get_settings") as get_settings:
        settings = MagicMock()
        settings.gcs_bucket = "my-bucket"
        settings.gcs_upload_timeout_seconds = 60
        get_settings.return_value = settings

        from dicom_middleware.infrastructure.gcs_storage import GCSStorageBackend

        backend = GCSStorageBackend()
        backend._client = mock_client
        uri = backend.save("1.2/3\\4", b"data")

    assert uri == "gs://my-bucket/studies/1.2_3_4.dcm"
    mock_bucket.blob.assert_called_once_with("studies/1.2_3_4.dcm")


def test_gcs_save_on_error_raises_runtime_error():
    """When upload raises, backend raises RuntimeError without leaking details."""
    mock_blob = MagicMock()
    mock_blob.upload_from_string.side_effect = Exception("sensitive internal message")
    mock_bucket = MagicMock()
    mock_bucket.name = "my-bucket"
    mock_bucket.blob.return_value = mock_blob
    mock_client = MagicMock()
    mock_client.bucket.return_value = mock_bucket

    with patch("dicom_middleware.infrastructure.gcs_storage.get_settings") as get_settings:
        settings = MagicMock()
        settings.gcs_bucket = "my-bucket"
        settings.gcs_upload_timeout_seconds = 60
        get_settings.return_value = settings

        from dicom_middleware.infrastructure.gcs_storage import GCSStorageBackend

        backend = GCSStorageBackend()
        backend._client = mock_client

        with pytest.raises(RuntimeError) as exc_info:
            backend.save("1.2.3", b"data")
        assert "GCS upload failed" in str(exc_info.value)
        assert "sensitive" not in str(exc_info.value)
