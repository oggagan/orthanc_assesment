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

---

## How to capture load test evidence for submission

You can submit one or more of the following.

### Option 1: Screenshot of Locust web UI (recommended)

1. Start the load test in **interactive** mode:
   ```bash
   locust -f load_test/locustfile.py --host=http://localhost:8000
   ```
2. Open **http://localhost:8089** in your browser.
3. Enter **Number of users** (e.g. 100) and **Spawn rate** (e.g. 50), then click **Start swarming**.
4. When the run has enough data, open the **Statistics** tab.
5. Take a screenshot showing the table with **Name**, **# reqs**, **Fails**, **Avg**, **Min**, **Max**, **Median**, **req/s**, and the **Response time percentiles** (50%, 95%, etc.).
6. Save as e.g. `docs/screenshots/06-load-test-results.png`.

### Option 2: Screenshot of CSV or summary file

1. Open `load_test/results/summary_stats.csv` in Excel (or a text editor).
2. Or open `load_test/results/LOAD_TEST_SUMMARY.md` in a viewer or browser.
3. Take a screenshot showing **throughput** (Requests/s) and **p95** (95% response time).
4. Save as e.g. `docs/screenshots/06-load-test-results.png`.

### Option 3: Attach files

- Attach **summary_stats.csv** and **LOAD_TEST_SUMMARY.md** from `load_test/results/` to your submission so the assessor can see throughput and latency numbers directly.
