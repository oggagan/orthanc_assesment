"""Integration tests for DLQ: force failure and assert message sent (with mocks)."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from dicom_middleware.domain.events import DLQPayload
from dicom_middleware.infrastructure.dlq import send_to_dlq


@pytest.mark.asyncio
async def test_send_to_dlq_calls_producer():
    with patch("dicom_middleware.infrastructure.dlq.get_dlq_producer") as get_prod:
        producer = AsyncMock()
        get_prod.return_value = producer
        payload = DLQPayload(
            original_payload={"test": True},
            error_reason="Storage write failure",
            correlation_id="cid-123",
        )
        await send_to_dlq(payload, "Storage write failure")
        producer.send_and_wait.assert_called_once()
        call_kwargs = producer.send_and_wait.call_args
        assert call_kwargs[1]["value"] == payload.to_json_bytes()
