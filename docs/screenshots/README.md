# Screenshots (evidence)

Capture these after running the app (see [Runbook](../operations/runbook.md)).

Place here (or attach as required):

1. **Orthanc UI** – Study visible after DICOM upload.
2. **DB records** – Query result or table view showing `studies` with `correlation_id` and metadata.
3. **Kafka messages** – Message in topic `dicom.metadata.v1` (e.g. from Kafka UI or consumer). When using GCS, the message should show `storage_path` as a `gs://` URI (e.g. `gs://your-bucket/studies/{StudyInstanceUID}.dcm`).
4. **Storage (local)** – Directory listing or path showing `StudyInstanceUID` in filename under `storage/studies/` or `/data/dicom/studies/`.
5. **Storage (GCS)** – When using `STORAGE_BACKEND=gcs`: GCS bucket (e.g. Cloud Console) showing objects under `studies/` with `StudyInstanceUID.dcm` filenames; optionally a Kafka message or middleware log line showing `gcs_upload_success` or `gs://` URI.
6. **Metrics endpoint** – Output of `GET /metrics` (Prometheus format). When using GCS, include metrics such as `dicom_middleware_storage_upload_total{backend="gcs",status="success"}` or the storage duration histogram with `backend="gcs"`.
7. **Load test results** – Throughput and p95 latency (e.g. from Locust or `load_test/results/`).

These support the assessment deliverables.
