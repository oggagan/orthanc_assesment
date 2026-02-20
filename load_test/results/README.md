# Load test results

Run the load test from project root with the middleware running (see [Runbook](../../docs/operations/runbook.md)).

**Commands:**

Interactive (open browser to start):

```bash
locust -f load_test/locustfile.py --host=http://localhost:8000
```

Headless (no UI):

```bash
locust -f load_test/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 50 -t 60s --csv=load_test/results/summary
```

On Windows use the same commands. Ensure Locust is installed: `pip install locust`.

**Place here:**

- CSV export from Locust (e.g. `summary_stats.csv`, `summary_failures.csv` after the headless run).
- Screenshot or summary with **throughput** (target ≥ 1000 req/s) and **p95 latency** (target < 500 ms).
