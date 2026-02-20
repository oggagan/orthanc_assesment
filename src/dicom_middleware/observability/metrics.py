"""Prometheus metrics for pipeline and API."""

from prometheus_client import Counter, Histogram

# Request and pipeline metrics
REQUEST_COUNT = Counter(
    "dicom_middleware_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "dicom_middleware_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
PIPELINE_SUCCESS = Counter(
    "dicom_middleware_pipeline_success_total",
    "Successful pipeline runs",
)
PIPELINE_FAILURE = Counter(
    "dicom_middleware_pipeline_failure_total",
    "Failed pipeline runs",
    ["reason"],
)
DLQ_MESSAGES = Counter(
    "dicom_middleware_dlq_messages_total",
    "Messages sent to DLQ",
    ["reason"],
)

# Storage upload (local and GCS)
STORAGE_UPLOAD_DURATION_SECONDS = Histogram(
    "dicom_middleware_storage_upload_duration_seconds",
    "Storage upload duration in seconds",
    ["backend"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)
STORAGE_UPLOAD_TOTAL = Counter(
    "dicom_middleware_storage_upload_total",
    "Storage uploads by backend and status",
    ["backend", "status"],
)
