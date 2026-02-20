# Architecture Decision Records

## ADR-1: Local storage for raw DICOM (POC)

**Decision:** Use the local filesystem for storing raw DICOM in the POC instead of Google Cloud Storage.

**Context:** The assessment allows a POC; avoiding GCS reduces setup and credential management on developer machines.

**Consequences:**
- No `google-cloud-storage` dependency; no GCS env vars.
- Storage path is configurable via `STORAGE_PATH`; in Docker a volume is mounted.
- Kafka event carries `storage_path` as a file URI (e.g. `file:///data/dicom/studies/...`).
- The storage layer is abstracted (save by Study Instance UID, return path) so a GCS backend can be added later without changing the pipeline.

---

## ADR-2: Study detection via polling

**Decision:** Use a background polling task that lists Orthanc studies and processes those not yet in our DB, rather than requiring Orthanc to call a webhook.

**Context:** Stock Orthanc does not expose a built-in “OnNewStudy” REST callback; configuring Lua or a plugin adds complexity.

**Consequences:**
- New studies are detected within the poll interval (e.g. 15 seconds).
- The ingestion endpoint `POST /api/v1/ingestion/studies` remains available for manual trigger or future Orthanc plugin integration.
- Idempotency by Study Instance UID ensures duplicate polling does not create duplicate records or events.

---

## ADR-3: Idempotency key

**Decision:** Use DICOM Study Instance UID as the idempotency key for DB and pipeline.

**Context:** The same study may be reported multiple times (polling or retries); we must ensure zero duplicate processing.

**Consequences:**
- DB upsert by `study_instance_uid` (ON CONFLICT DO UPDATE).
- Kafka producer is configured with idempotence; duplicate keys result in a single message.
- Pipeline can be run again for the same study without creating duplicate rows or events.

---

## ADR-4: Error response shape

**Decision:** Use a consistent RFC 7807–style JSON body for all 4xx/5xx responses: `type`, `title`, `status`, `detail`, `correlation_id`, `timestamp`, optional `errors`.

**Context:** API documentation and clients benefit from a single, documented error contract.

**Consequences:**
- All exception handlers produce this shape; OpenAPI documents it.
- Correlation ID is included when available for tracing.

---

## ADR-5: Correlation ID propagation

**Decision:** Generate a correlation ID at the ingestion boundary and propagate it in logs, DB row, Kafka message body, and Kafka headers.

**Context:** Full traceability is required for production-grade observability.

**Consequences:**
- Middleware sets or forwards `X-Correlation-ID` and stores it in a context variable.
- Every structured log line can include `correlation_id`; DB and Kafka events store it explicitly.

---

## ADR-6: GCS as optional storage backend

**Decision:** Support Google Cloud Storage as an optional backend for raw DICOM, selectable via `STORAGE_BACKEND`; local remains the default.

**Context:** Need to support cloud storage for production while keeping local for dev and existing deployments.

**Consequences:**
- Config validation when GCS is selected (e.g. `GCS_BUCKET` required); app fails fast at startup if misconfigured.
- Observability (metrics, structured logging) for both local and GCS backends.
- Credentials via standard `GOOGLE_APPLICATION_CREDENTIALS`; no key path in application config.
- Pipeline unchanged except backend injection via `get_storage_backend()`; Kafka event `storage_path` is either `file://` or `gs://` depending on backend.
