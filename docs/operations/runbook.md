# Runbook

Commands and steps to run, verify, and troubleshoot the middleware (local or GCS). Quick command list: [commands.md](commands.md).

## Run locally (local storage)

1. **Prerequisites:** Docker Desktop running.
2. **From project root**, copy env (pick one):
   - **Unix:** `cp .env.example .env`
   - **Windows (PowerShell):** `Copy-Item .env.example .env`
3. **Start:** `docker-compose up --build`
4. **URLs:** Middleware http://localhost:8000, Orthanc UI http://localhost:8042, Kafka localhost:9092, PostgreSQL localhost:5432.

## Verify health

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:8000/ready
# Expected: {"status":"ok"}

curl -s http://localhost:8000/metrics
# Expected: Prometheus text (e.g. dicom_middleware_...)
```

## Upload a DICOM

**Option A:** Use Orthanc web UI (http://localhost:8042) to upload a DICOM file. The background poller will detect the new study within ~15 s and run the pipeline.

**Option B:** Manual trigger. Get the Orthanc study ID from the Orthanc UI, then:

```bash
curl -X POST http://localhost:8000/api/v1/ingestion/studies -H "Content-Type: application/json" -d "{\"ID\": \"<study-id>\", \"Path\": \"Study\"}"
```

Replace `<study-id>` with the actual Orthanc study ID.

## Using GCS storage

1. **Ensure `creds.json`** is in the project root (not committed; add to `.gitignore`).
2. **In `.env`:** set `STORAGE_BACKEND=gcs`, `GCS_BUCKET=your-bucket`, and optionally `GCS_PROJECT`, `GCS_UPLOAD_TIMEOUT_SECONDS`. For Docker, set `GOOGLE_APPLICATION_CREDENTIALS=/app/creds.json`.
3. **Start:** from project root run:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.gcs.yml up --build
   ```
   (Same on Windows PowerShell.) Ensure `GCS_BUCKET` is set in `.env` or the environment.
4. **Verify:** Check the GCS bucket for objects under `studies/`, or run health curl and trigger one study via ingestion API.

## Troubleshooting

- **DLQ:** If processing fails, check Kafka topic `dicom.metadata.dlq` for messages (original_payload, error_reason, correlation_id). Check middleware logs for the same correlation_id.
- **DB:** Connect to PostgreSQL and query `studies`; ensure `correlation_id` and metadata are present. Example (replace container name if different):
  ```bash
  docker exec assesment-postgres-1 psql -U postgres -d dicom -c "SELECT id, correlation_id, study_instance_uid, patient_id, modality, study_date FROM studies LIMIT 5;"
  ```
- **Storage (local):** Raw DICOM is under the volume (e.g. `./storage` or container `/data/dicom`). Ensure `STORAGE_PATH` is writable.
- **Storage (GCS):** If GCS upload fails, check DLQ for "Storage write failure", metrics `dicom_middleware_storage_upload_total{backend="gcs",status="failure"}`, and that `GOOGLE_APPLICATION_CREDENTIALS` is set and the service account has Storage Object Creator on the bucket.
- **Kafka:** List topics (replace container name if different):
  ```bash
  docker exec assesment-kafka-1 kafka-topics --bootstrap-server localhost:29092 --list
  ```

## Load test

From project root with middleware running:

```bash
locust -f load_test/locustfile.py --host=http://localhost:8000
```

For headless run: `locust -f load_test/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 50 -t 60s --csv=load_test/results/summary`

See [load_test/results/README.md](../../load_test/results/README.md) for details and where to place results.
