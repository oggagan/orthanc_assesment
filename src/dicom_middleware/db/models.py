"""Canonical database schema. Raw DICOM is never stored; metadata only."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class StudyRecord(Base):
    """Canonical study metadata record."""

    __tablename__ = "studies"
    __table_args__ = (UniqueConstraint("study_instance_uid", name="uq_study_instance_uid"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    correlation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    study_instance_uid: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    patient_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    modality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    study_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
