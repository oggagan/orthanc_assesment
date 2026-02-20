# Data flow

## End-to-end sequence

1. **Trigger:** Orthanc has a new study (uploaded via UI or C-STORE), or a client POSTs to `/api/v1/ingestion/studies` with Orthanc study ID.
2. **Correlation ID:** Generated at the ingestion boundary (middleware) and set in context; added to response header `X-Correlation-ID`.
3. **Fetch DICOM:** Middleware calls Orthanc REST to get the first instance file (or study archive) as bytes.
4. **Extract metadata:** pydicom parses the bytes and extracts only Study Instance UID, Patient ID, Modality, Study Date. On parse/validation failure → DLQ.
5. **Persist metadata:** Upsert into PostgreSQL by Study Instance UID (idempotent). On failure → DLQ.
6. **Store raw DICOM:** Write bytes to `{STORAGE_PATH}/studies/{StudyInstanceUID}.dcm`. On failure → DLQ.
7. **Publish event:** Send to Kafka topic `dicom.metadata.v1` with correlation_id, metadata, storage_path, timestamp. Producer is idempotent and acks=all. On failure → DLQ.
8. **DLQ:** Any failure in steps 4–7 results in a message to `dicom.metadata.dlq` with original payload, error reason, and correlation ID.

## Event payload (Kafka)

- `correlation_id`, `study_instance_uid`, `patient_id`, `modality`, `study_date`, `storage_path` (e.g. `file:///data/dicom/studies/...`), `timestamp` (ISO).

## DLQ payload

- `original_payload`, `error_reason`, `correlation_id`.

Commands to run the stack: [Runbook](../operations/runbook.md).
