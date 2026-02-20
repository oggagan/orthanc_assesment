"""Background poller: detect new studies in Orthanc and run pipeline (alternative to webhook)."""

import asyncio
from uuid import uuid4

from dicom_middleware.db.session import get_session_factory
from dicom_middleware.infrastructure.orthanc import OrthancClient
from dicom_middleware.observability.logging import get_logger
from dicom_middleware.application.use_cases import process_new_study
from dicom_middleware.infrastructure.repository import exists_by_study_instance_uid

_log = get_logger(__name__)

POLL_INTERVAL_SEC = 15


async def _process_study_if_new(orthanc_study_id: str) -> None:
    """If this study is not yet in our DB, run pipeline."""
    factory = get_session_factory()
    async with factory() as session:
        client = OrthancClient()
        try:
            study_instance_uid = await client.get_study_instance_uid(orthanc_study_id)
        except Exception as e:
            _log.warning("orthanc_get_uid_failed", orthanc_study_id=orthanc_study_id, error=str(e))
            return
        if not study_instance_uid:
            return
        exists = await exists_by_study_instance_uid(session, study_instance_uid)
        if exists:
            return
        correlation_id = str(uuid4())
        try:
            await process_new_study(correlation_id, orthanc_study_id, session)
        except Exception as e:
            _log.warning(
                "poller_pipeline_failed",
                orthanc_study_id=orthanc_study_id,
                correlation_id=correlation_id,
                error=str(e),
            )


async def run_orthanc_poller() -> None:
    """Poll Orthanc for new studies and process them. Runs until cancelled."""
    client = OrthancClient()
    while True:
        try:
            study_ids = await client.get_study_ids()
            for sid in study_ids:
                await _process_study_if_new(sid)
        except asyncio.CancelledError:
            break
        except Exception as e:
            _log.warning("orthanc_poller_error", error=str(e))
        await asyncio.sleep(POLL_INTERVAL_SEC)
