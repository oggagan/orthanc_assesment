# Observability component

**Correlation ID:** Generated or forwarded at the ingestion boundary; stored in a context variable. Propagated to: response header `X-Correlation-ID`, every structured log line, DB row, Kafka message body and headers.

**Logging:** Structured JSON only (structlog). Each log event includes `correlation_id` when in request context. Configured log level via `LOG_LEVEL`.

**Health:** `GET /health` – liveness. `GET /ready` – readiness (currently returns 200; can be extended to check DB and Kafka).

**Metrics:** `GET /metrics` – Prometheus format. Exposed counters/histograms include request count, request latency, pipeline success/failure, DLQ message count. Use for throughput and p95 latency evidence.
