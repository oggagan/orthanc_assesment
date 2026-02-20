"""PostgreSQL repository: idempotent upsert by study_instance_uid."""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.db.models import StudyRecord
from dicom_middleware.domain.entities import StudyMetadata


async def upsert_study(
    session: AsyncSession,
    correlation_id: UUID,
    metadata: StudyMetadata,
) -> None:
    """
    Insert or ignore study by study_instance_uid (idempotent).
    Uses ON CONFLICT DO NOTHING so duplicate processing creates no extra row.
    """
    stmt = insert(StudyRecord).values(
        correlation_id=correlation_id,
        study_instance_uid=metadata.study_instance_uid,
        patient_id=metadata.patient_id,
        modality=metadata.modality,
        study_date=metadata.study_date,
    ).on_conflict_do_update(
        index_elements=["study_instance_uid"],
        set_={
            "patient_id": metadata.patient_id,
            "modality": metadata.modality,
            "study_date": metadata.study_date,
        },
    )
    await session.execute(stmt)
    await session.commit()


async def exists_by_study_instance_uid(session: AsyncSession, study_instance_uid: str) -> bool:
    """Return True if a record with this UID already exists."""
    r = await session.execute(
        select(StudyRecord.id).where(StudyRecord.study_instance_uid == study_instance_uid).limit(1)
    )
    return r.scalar() is not None
