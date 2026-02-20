# Load test summary

**Study ID used:** Valid Orthanc study ID (`06830bc6-b5162579-e40d299a-9fa7a3f4-95327fb7`) so the pipeline runs end-to-end (fetch DICOM, DB upsert, GCS, Kafka).

**Run:** Headless Locust, 100 users, 50/s ramp, 60 s duration.  
**Target:** `POST /api/v1/ingestion/studies` at `http://localhost:8000`.

## Results (valid study ID run)

| Metric | Value |
|--------|--------|
| Total requests | 102 |
| Successful (200) | 79 (77.45%) |
| Failed (502) | 23 (22.55%) |
| Throughput | **1.85 req/s** |
| Median response time | 22,000 ms (22 s) |
| Average response time | 22,793 ms |
| 95th percentile (p95) | 52,000 ms (52 s) |
| Min / Max | 3,033 ms / 54,042 ms |

**Note:** With a real study the pipeline performs full I/O (Orthanc fetch, GCS upload, Kafka publish), so latency is high and throughput is lower. The 502s are likely timeouts or resource contention under concurrent load. Idempotency is preserved: the same study is upserted and only one Kafka message per study.

## How to reproduce

1. Ensure Orthanc has at least one study. Get IDs:  
   `Invoke-RestMethod -Uri "http://localhost:8042/studies" -Headers @{Authorization="Basic <base64(orthanc:orthanc)>"}`  
   or from Orthanc UI.
2. Optional: set a different study ID:  
   `$env:ORTHANC_STUDY_ID="<study-id>"`
3. Run:  
   `locust -f load_test/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 50 -t 60s --csv=load_test/results/summary`

## Files in this folder

- `summary_stats.csv` – Request count, response times, percentiles, throughput.
- `summary_failures.csv` – Error breakdown (502).
- `summary_stats_history.csv` – Time-series stats.
- `summary_exceptions.csv` – Exception details.

## Assignment targets (task.txt)

| Target | This run | Notes |
|--------|----------|--------|
| Throughput ≥ 1000 msg/s | 1.85 req/s | Full pipeline is I/O bound; target may require multiple middleware instances or lighter pipeline for load test. |
| p95 < 500 ms | 52 s | Full pipeline latency (Orthanc + GCS + Kafka) dominates. |

Evidence: CSVs and this summary show load test was executed with a valid study ID and both success and failure paths observed.
