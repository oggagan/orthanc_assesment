# Orthanc integration

**Purpose:** Communicate with Orthanc REST API to list studies and retrieve DICOM data.

**Detection of new studies:**
- **Polling:** A background task runs every 15 seconds, calls `GET /studies`, and for each Orthanc study ID checks if the corresponding Study Instance UID already exists in our DB; if not, runs the pipeline.
- **Webhook (optional):** If Orthanc is configured to POST to our ingestion endpoint when a study is stored, the middleware processes it immediately.

**REST calls used:**
- `GET {ORTHANC_URL}/studies` – list Orthanc study IDs.
- `GET {ORTHANC_URL}/studies/{id}` – get study info (including MainDicomTags.StudyInstanceUID).
- `GET {ORTHANC_URL}/instances/{instance_id}/file` – get DICOM file bytes (used for first instance of a study).

**Configuration:** `ORTHANC_URL` (e.g. `http://orthanc:8042` in Docker).
