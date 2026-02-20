"""Use case: process new study (ingestion entry point)."""

from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.application.pipeline import run_pipeline


async def process_new_study(
    correlation_id: str,
    orthanc_study_id: str,
    session: AsyncSession,
) -> None:
    """Process a new study: run pipeline (extract -> DB -> storage -> Kafka). Idempotent by study_instance_uid."""
    await run_pipeline(correlation_id, orthanc_study_id, session)
