"""Application configuration via environment variables."""

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Orthanc
    orthanc_url: str = Field(default="http://orthanc:8042", description="Orthanc REST API base URL")
    orthanc_username: str | None = Field(default=None, description="Orthanc HTTP auth username (e.g. orthanc)")
    orthanc_password: str | None = Field(default=None, description="Orthanc HTTP auth password (e.g. orthanc)")

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092", description="Kafka broker list")
    kafka_topic: str = Field(default="dicom.metadata.v1", description="Metadata event topic")
    kafka_dlq_topic: str = Field(default="dicom.metadata.dlq", description="Dead letter queue topic")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/dicom",
        description="Async PostgreSQL connection URL",
    )

    # Storage backend: local (default) or gcs
    storage_backend: Literal["local", "gcs"] = Field(
        default="local",
        description="Storage backend for raw DICOM: local filesystem or GCS",
    )
    storage_path: Path = Field(
        default=Path("./storage"),
        description="Base directory for raw DICOM (local only); path: {storage_path}/studies/{StudyInstanceUID}.dcm",
    )

    # GCS (used only when storage_backend=gcs)
    gcs_bucket: str | None = Field(
        default=None,
        description="GCS bucket name (required when storage_backend=gcs)",
    )
    gcs_project: str | None = Field(
        default=None,
        description="GCP project ID (optional; can be inferred from credentials)",
    )
    gcs_upload_timeout_seconds: int = Field(
        default=60,
        ge=5,
        le=300,
        description="Timeout in seconds for GCS upload",
    )

    # Observability
    log_level: str = Field(default="INFO", description="Logging level")
    metrics_port: int | None = Field(default=None, description="Optional separate port for metrics; same app if unset")

    @model_validator(mode="after")
    def validate_gcs_config(self) -> "Settings":
        if self.storage_backend == "gcs" and not (self.gcs_bucket and self.gcs_bucket.strip()):
            raise ValueError("GCS_BUCKET is required when STORAGE_BACKEND=gcs")
        return self


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return cached settings (load from env on first call)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
