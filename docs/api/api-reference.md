# API reference

Base URL (local): `http://localhost:8000`.

**For full request/response schemas and examples**, see the interactive OpenAPI docs at **`/docs`** (Swagger UI) and **`/redoc`**, or fetch **`GET /openapi.json`** for the machine-readable spec. To run the API locally, see [Runbook](../operations/runbook.md).

## Versioning

- API is versioned under `/api/v1`. Health and metrics are unversioned: `/health`, `/ready`, `/metrics`.

## Endpoints

### Health and readiness

| Method | Path    | Description                    |
|--------|---------|--------------------------------|
| GET    | /health | Liveness; returns 200 if up.   |
| GET    | /ready  | Readiness; returns 200.       |
| GET    | /metrics | Prometheus scrape endpoint. |

### Ingestion

| Method | Path                        | Description |
|--------|-----------------------------|-------------|
| POST   | /api/v1/ingestion/studies   | Accept Orthanc study notification; body `{"ID": "<orthanc-study-id>", "Path": "Study"}` (Path optional). Returns `{"status": "accepted", "correlation_id": "..."}`. |

**Response headers:** `X-Correlation-ID` is set on all responses.

## Error responses

All 4xx/5xx responses use a single JSON shape:

- `type` (optional): Error code or URI.
- `title`: Short summary.
- `status`: HTTP status code.
- `detail`: Human-readable detail.
- `correlation_id`: Request correlation ID when available.
- `timestamp`: ISO 8601.
- `errors` (optional): Validation or field-level errors.

Example:

```json
{
  "type": "validation_error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2025-02-19T12:00:00.000000Z",
  "errors": []
}
```
