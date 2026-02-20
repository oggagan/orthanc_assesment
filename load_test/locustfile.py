"""Locust load test for ingestion API.
Run: locust -f load_test/locustfile.py --host=http://localhost:8000
Target: >= 1000 msg/sec and p95 latency < 500ms (tune workers accordingly).
"""

from locust import HttpUser, task, between


class IngestionUser(HttpUser):
    """Simulate Orthanc webhook calls to POST /api/v1/ingestion/studies."""

    wait_time = between(0, 0.1)

    @task
    def ingest_study(self):
        self.client.post(
            "/api/v1/ingestion/studies",
            json={"ID": "test-study-id", "Path": "Study"},
            name="/api/v1/ingestion/studies",
        )
