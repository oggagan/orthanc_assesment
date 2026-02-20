# DICOM Middleware POC

Proof of concept for controlled DICOM ingestion using **Orthanc**, metadata extraction, canonical persistence in **PostgreSQL**, event publication to **Apache Kafka**, and raw DICOM storage (local filesystem or **GCS**). Built with **Python FastAPI**.

## Features

- **DICOM ingestion:** Upload DICOM to Orthanc; middleware detects new studies (polling or webhook) and processes them.
- **Metadata extraction:** Study Instance UID, Patient ID, Modality, Study Date (pydicom).
- **Canonical DB:** Metadata only; raw DICOM never stored in the database. Idempotent upsert by Study Instance UID.
- **Raw DICOM storage:** Local path or GCS bucket (`STORAGE_BACKEND=local` or `gcs`).
- **Kafka:** Events to `dicom.metadata.v1` with correlation ID, metadata, storage path, timestamp. Idempotent producer, acks=all.
- **DLQ:** Failures send to `dicom.metadata.dlq` with original payload, error reason, correlation ID.
- **Observability:** Correlation ID in logs, DB, Kafka; structured JSON logging; `/health`, `/ready`, `/metrics`.

## Quick start

1. **Prerequisites:** Docker Desktop, Python 3.11+ (for local run and tests).
2. **From project root:** copy env and start (pick one):
   - **Unix:** `cp .env.example .env && docker-compose up --build`
   - **Windows (PowerShell):** `Copy-Item .env.example .env; docker-compose up --build`
3. **Endpoints:** Middleware http://localhost:8000, Orthanc UI http://localhost:8042, API docs http://localhost:8000/docs.
4. **Verify:** `curl http://localhost:8000/health` → `{"status":"ok"}`. Upload a DICOM via Orthanc UI or trigger manually: `curl -X POST http://localhost:8000/api/v1/ingestion/studies -H "Content-Type: application/json" -d "{\"ID\": \"<orthanc-study-id>\", \"Path\": \"Study\"}"`.

**Run with GCS:** See [Run with GCS](docs/operations/runbook.md#using-gcs-storage). Set `STORAGE_BACKEND=gcs`, `GCS_BUCKET`, and `GOOGLE_APPLICATION_CREDENTIALS` in `.env`; put `creds.json` in project root; then run `docker-compose -f docker-compose.yml -f docker-compose.gcs.yml up --build`.

Full steps and troubleshooting: [Runbook](docs/operations/runbook.md). Quick command list: [commands.md](docs/operations/commands.md).

## Project layout

- `src/dicom_middleware/` – FastAPI app, API, pipeline, domain, infrastructure (Orthanc, DICOM extract, DB, storage, Kafka, DLQ).
- `docs/` – [Architecture](docs/architecture/overview.md), [ADR](docs/architecture/decisions/ADR.md), [API reference](docs/api/api-reference.md), [components](docs/components/component-catalog.md), [runbook](docs/operations/runbook.md), [configuration](docs/operations/configuration.md).
- `tests/` – Unit and integration tests.
- `load_test/` – Locust script and [results](load_test/results/README.md).

## Design decisions

- **Storage:** Local or GCS; abstracted so backends are pluggable. See [ADR-1](docs/architecture/decisions/ADR.md), [ADR-6](docs/architecture/decisions/ADR.md).
- **Polling:** Background task polls Orthanc; ingestion endpoint for manual or webhook. See [ADR-2](docs/architecture/decisions/ADR.md).
- **Idempotency:** Study Instance UID is the key. See [ADR-3](docs/architecture/decisions/ADR.md).

## Tests

Set `PYTHONPATH` then run (from project root):

- **Unix:** `export PYTHONPATH=src` then `pytest tests/ -v --ignore=tests/e2e`
- **Windows (PowerShell):** `$env:PYTHONPATH="src"; pytest tests/ -v --ignore=tests/e2e`

Install deps first: `pip install -r requirements.txt -r requirements-dev.txt`.

## Evidence and screenshots

See [docs/screenshots/README.md](docs/screenshots/README.md) for what to capture (Orthanc UI, DB, Kafka, storage, metrics, load test) and where to place files.

## License

Internal POC / assessment.
