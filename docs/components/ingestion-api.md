# Ingestion API component

**Purpose:** Accept notifications of new DICOM studies (from Orthanc or manual call) and trigger the processing pipeline.

**Entry point:** `POST /api/v1/ingestion/studies`.

**Request body:** `{"ID": "<orthanc-study-id>", "Path": "Study"}`. `ID` is required (Orthanc internal study ID); `Path` is optional.

**Behavior:**
- Correlation ID is set by middleware (or taken from `X-Correlation-ID` if present).
- A DB session is obtained via dependency injection; the use case `process_new_study` is invoked with correlation ID, Orthanc study ID, and session.
- Response: `{"status": "accepted", "correlation_id": "..."}` on success; 502 with error body if the pipeline fails.
- Idempotency: same study ID processed twice results in a single DB row and a single Kafka message (enforced by pipeline and DB upsert).

**See:** [API reference](../api/api-reference.md), [pipeline.md](pipeline.md).
