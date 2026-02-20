# Messaging component

**Topics:**
- `dicom.metadata.v1`: Successfully processed study events (correlation_id, study_instance_uid, patient_id, modality, study_date, storage_path, timestamp).
- `dicom.metadata.dlq`: Failed processing (original_payload, error_reason, correlation_id).

**Producer settings:**
- Idempotence enabled; `acks=all`.
- Correlation ID is set in Kafka message headers for `dicom.metadata.v1`.

**DLQ triggers:** Metadata parsing failure, DB write failure, storage write failure, schema validation failure, Kafka publish failure.

**Configuration:** `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`, `KAFKA_DLQ_TOPIC`.
