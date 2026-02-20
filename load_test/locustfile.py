"""Locust load test for ingestion API.
Run: locust -f load_test/locustfile.py --host=http://localhost:8000
Use a valid Orthanc study ID so the pipeline returns 200: set env ORTHANC_STUDY_ID, or one is used by default.
Target: >= 1000 msg/sec and p95 latency < 500ms (tune workers accordingly).
"""

import os
from locust import HttpUser, task, between

# Use a valid study ID from Orthanc so pipeline succeeds (200); override with env ORTHANC_STUDY_ID
VALID_STUDY_ID = os.environ.get("ORTHANC_STUDY_ID", "06830bc6-b5162579-e40d299a-9fa7a3f4-95327fb7")


class IngestionUser(HttpUser):
    """Simulate Orthanc webhook calls to POST /api/v1/ingestion/studies."""

    wait_time = between(0, 0.1)

    @task
    def ingest_study(self):
        self.client.post(
            "/api/v1/ingestion/studies",
            json={"ID": VALID_STUDY_ID, "Path": "Study"},
            name="/api/v1/ingestion/studies",
        )
