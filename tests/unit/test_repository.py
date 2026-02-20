"""Unit tests for repository (require DB; can be run with testcontainers or mocked session)."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.domain.entities import StudyMetadata
from dicom_middleware.infrastructure.repository import upsert_study, exists_by_study_instance_uid


@pytest.mark.asyncio
async def test_upsert_study_calls_session():
    session = AsyncMock(spec=AsyncSession)
    meta = StudyMetadata(study_instance_uid="1.2.3", patient_id="P1", modality="CT", study_date="20250101")
    cid = uuid4()
    await upsert_study(session, cid, meta)
    session.execute.assert_called_once()
    session.commit.assert_called_once()
