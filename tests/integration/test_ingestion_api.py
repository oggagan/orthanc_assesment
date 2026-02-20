"""Integration tests for ingestion API (app + mocked infra or real services)."""

import pytest
from httpx import ASGITransport, AsyncClient

from dicom_middleware.main import app


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_returns_200(client: AsyncClient):
    r = await client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_metrics_returns_prometheus(client: AsyncClient):
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")
    assert "dicom_middleware" in r.text or "#" in r.text


@pytest.mark.asyncio
async def test_ingestion_accepts_post_and_returns_correlation_id(client: AsyncClient):
    r = await client.post(
        "/api/v1/ingestion/studies",
        json={"ID": "non-existent-orthanc-id", "Path": "Study"},
    )
    # May be 502 if Orthanc unreachable or 200/202 if accepted
    assert r.status_code in (200, 202, 502)
    if r.status_code in (200, 202):
        data = r.json()
        assert "correlation_id" in data or "status" in data
    assert "X-Correlation-ID" in r.headers
