# Architecture overview

The DICOM Middleware POC is a FastAPI application that sits between Orthanc (DICOM server) and downstream systems. It does not store raw DICOM in the database; it extracts metadata, persists it in PostgreSQL, stores raw DICOM on local disk (or pluggable storage), and publishes events to Kafka.

## High-level diagram

```
Orthanc (DICOM)  -->  Middleware (FastAPI)  -->  PostgreSQL (metadata only)
                              |
                              +----------------->  Local storage (raw DICOM)
                              |
                              +----------------->  Kafka (dicom.metadata.v1)
                              |
                              +----------------->  DLQ (dicom.metadata.dlq) on failure
```

## Layers

- **Presentation:** API routes (`/health`, `/ready`, `/metrics`, `/api/v1/ingestion/studies`), OpenAPI, error handling, correlation ID middleware.
- **Application:** Use case “process new study”, pipeline orchestration (extract → DB → storage → Kafka), DLQ on failure.
- **Domain:** Study metadata entity, Kafka event and DLQ payload schemas.
- **Infrastructure:** Orthanc client, DICOM metadata extraction (pydicom), PostgreSQL repository, local filesystem storage, Kafka producer, DLQ producer.

## Detection of new studies

- **Polling:** A background task polls Orthanc `/studies` periodically and processes any study not yet present in the canonical DB (by Study Instance UID). Correlation ID is generated when the study is first processed.
- **Webhook (optional):** If Orthanc is configured to POST to `POST /api/v1/ingestion/studies` with body `{"ID": "<orthanc-study-id>"}`, the middleware processes that study immediately. Correlation ID is set by the middleware (or forwarded from the request header).

## Compliance

- Raw DICOM is never stored in the database.
- Only the middleware writes to the canonical DB (no direct Orthanc → DB).
- All flows are idempotent (by Study Instance UID); duplicate processing is zero.
- Correlation ID is propagated in logs, DB, and Kafka headers.

To run the stack: [Runbook](../operations/runbook.md).
