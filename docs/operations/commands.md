# Commands quick reference

Copy-paste commands from project root. For full steps see [runbook.md](runbook.md).

## Copy env

- **Unix:** `cp .env.example .env`
- **Windows (PowerShell):** `Copy-Item .env.example .env`

## Start (local storage)

```bash
docker-compose up --build
```

## Start (GCS storage)

Ensure `.env` has `STORAGE_BACKEND=gcs`, `GCS_BUCKET`, and `creds.json` is in project root. Then:

```bash
docker-compose -f docker-compose.yml -f docker-compose.gcs.yml up --build
```

## Verify

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/api/v1/ingestion/studies -H "Content-Type: application/json" -d "{\"ID\": \"<orthanc-study-id>\", \"Path\": \"Study\"}"
```

## Tests

Set PYTHONPATH then run pytest:

- **Unix:** `export PYTHONPATH=src` then `pytest tests/ -v --ignore=tests/e2e`
- **Windows (PowerShell):** `$env:PYTHONPATH="src"; pytest tests/ -v --ignore=tests/e2e`

## Load test

```bash
locust -f load_test/locustfile.py --host=http://localhost:8000
```

Headless: `locust -f load_test/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 50 -t 60s --csv=load_test/results/summary`
