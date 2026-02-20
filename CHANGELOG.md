# Changelog

## [0.1.0] – 2025-02-19

### Added

- FastAPI application with `/health`, `/ready`, `/metrics`, `/api/v1/ingestion/studies`.
- Orthanc integration: REST client, background poller for new studies.
- DICOM metadata extraction (pydicom): Study Instance UID, Patient ID, Modality, Study Date.
- Canonical PostgreSQL schema and idempotent upsert by Study Instance UID.
- Local filesystem storage for raw DICOM at `{STORAGE_PATH}/studies/{StudyInstanceUID}.dcm`.
- Kafka producer (idempotent, acks=all) for topic `dicom.metadata.v1` with correlation_id in headers.
- Dead letter queue `dicom.metadata.dlq` on metadata/DB/storage/Kafka failures.
- Correlation ID middleware and propagation in logs, DB, Kafka.
- Structured JSON logging (structlog), Prometheus metrics, RFC 7807–style error responses.
- Docker Compose: Orthanc, Zookeeper, Kafka, PostgreSQL, middleware with volume for storage.
- Unit and integration tests including DLQ on storage failure.
- Load test script (Locust) and results placeholder.
- Documentation: architecture, ADR, API reference, component catalog, runbook, configuration.
