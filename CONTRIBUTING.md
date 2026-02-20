# Contributing

## Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     pip install -r requirements.txt -r requirements-dev.txt
     $env:PYTHONPATH = "src"
     ```
   - **Unix:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt -r requirements-dev.txt
     export PYTHONPATH=src
     ```
3. Copy `.env.example` to `.env` and adjust for local runs (e.g. Kafka/Postgres via Docker).

## Running the app

- **With Docker:** See [Runbook](docs/operations/runbook.md).
- **App only (no Docker):** From project root, set `PYTHONPATH=src` then run `uvicorn dicom_middleware.main:app --reload --host 0.0.0.0`. Ensure Kafka and Postgres are reachable (e.g. run only postgres and kafka via docker-compose).

## Tests

Set `PYTHONPATH=src` first (see Setup). From project root:

```bash
pytest tests/ -v --ignore=tests/e2e
```

## Code style

- Layered structure: API → application → domain → infrastructure.
- Use type hints and Pydantic for request/response and events.
- Correlation ID must be propagated in any new path that touches the pipeline.

## Documentation

- Update `docs/` when adding endpoints, components, or config. Keep ADR for significant decisions.
