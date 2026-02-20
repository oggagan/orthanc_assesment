# Persistence component

**Canonical database (PostgreSQL):**
- Table `studies`: `id`, `correlation_id` (UUID), `study_instance_uid` (UNIQUE), `patient_id`, `modality`, `study_date`, `created_at`.
- Raw DICOM is never stored in the DB.
- Writes are idempotent (upsert by `study_instance_uid`).

**Raw DICOM storage (backend selectable via `STORAGE_BACKEND`):**
- **Local (default):** Base directory `STORAGE_PATH` (e.g. `/data/dicom` in Docker, `./storage` locally). Path per study: `{STORAGE_PATH}/studies/{StudyInstanceUID}.dcm`. Directory is created if missing; file is overwritten on re-run (idempotent). Kafka event `storage_path` is a `file://` URI.
- **GCS:** Bucket and path `gs://{GCS_BUCKET}/studies/{StudyInstanceUID}.dcm`. Kafka event `storage_path` is a `gs://` URI. Backend is chosen by config; see `storage_factory.get_storage_backend()` and [configuration](../operations/configuration.md).

**See:** ADR-1 (local storage), ADR-6 (GCS optional backend), [architecture overview](../architecture/overview.md).
