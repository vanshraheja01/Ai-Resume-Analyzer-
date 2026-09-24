import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.resume import Resume


class Match(Base):
    """Result of running the AI matching engine on one (resume, job) pair.
    Re-running a match on the same pair should update this row, not duplicate it."""

    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("resume_id", "job_id", name="uq_resume_job_match"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    matched_skills: Mapped[list[str] | None] = mapped_column(JSONB)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSONB)
    partial_skills: Mapped[list[str] | None] = mapped_column(JSONB)
    recommendations: Mapped[list[str] | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="matches")
    job: Mapped["Job"] = relationship(back_populates="matches")
