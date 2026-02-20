# Pipeline component

**Purpose:** Run the full processing flow for one study: fetch DICOM from Orthanc → extract metadata → persist to DB → store raw DICOM locally → publish to Kafka. On any failure, send to DLQ.

**Steps:**
1. Fetch DICOM bytes from Orthanc (first instance of the study).
2. Extract metadata (Study Instance UID, Patient ID, Modality, Study Date) with pydicom; on parse/validation failure → DLQ ("Metadata parsing failure").
3. Upsert canonical record in PostgreSQL by Study Instance UID; on failure → DLQ ("DB write failure").
4. Write raw DICOM to `{STORAGE_PATH}/studies/{StudyInstanceUID}.dcm`; on failure → DLQ ("Storage write failure").
5. Publish event to `dicom.metadata.v1` with correlation_id, metadata, storage_path, timestamp; on failure → DLQ ("Kafka publish failure").

**Idempotency:** Study Instance UID is the key; duplicate runs produce a single DB row and (with idempotent producer) a single Kafka message.

**See:** [persistence.md](persistence.md), [messaging.md](messaging.md).
