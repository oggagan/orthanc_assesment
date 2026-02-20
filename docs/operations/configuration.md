# Configuration reference

For commands to start the app (local or GCS), see [Runbook](runbook.md).

All configuration is via environment variables (no secrets in repo). Example: `.env.example`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| ORTHANC_URL | No | http://orthanc:8042 | Orthanc REST API base URL |
| ORTHANC_USERNAME | No | (none) | Orthanc HTTP Basic auth username (e.g. orthanc) |
| ORTHANC_PASSWORD | No | (none) | Orthanc HTTP Basic auth password (e.g. orthanc) |
| KAFKA_BOOTSTRAP_SERVERS | No | localhost:9092 | Comma-separated Kafka brokers |
| KAFKA_TOPIC | No | dicom.metadata.v1 | Metadata event topic |
| KAFKA_DLQ_TOPIC | No | dicom.metadata.dlq | Dead letter queue topic |
| DATABASE_URL | No | postgresql+asyncpg://postgres:postgres@localhost:5432/dicom | Async PostgreSQL URL |
| STORAGE_BACKEND | No | local | Storage backend: `local` or `gcs` |
| STORAGE_PATH | No | ./storage | Base directory for raw DICOM (local backend only) |
| GCS_BUCKET | When STORAGE_BACKEND=gcs | (none) | GCS bucket name |
| GCS_PROJECT | No | (none) | GCP project ID (optional; can be inferred from credentials) |
| GCS_UPLOAD_TIMEOUT_SECONDS | No | 60 | Timeout in seconds for GCS upload (5–300) |
| LOG_LEVEL | No | INFO | Logging level |

**GCS:** When `STORAGE_BACKEND=gcs`, set `GOOGLE_APPLICATION_CREDENTIALS` to the path of the service account JSON key file. The app does not read the key path from config; use the standard env var. On GKE with workload identity, the env var may be unset and default credentials are used.

**Docker Compose:** The `middleware` service sets these in `docker-compose.yml`; override with an env file or host environment if needed. Copy `.env.example` to `.env` and set variables as needed; do not commit `.env` or `creds.json`.
