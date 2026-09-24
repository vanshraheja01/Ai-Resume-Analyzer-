import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate
from app.services.ai_service import AIProviderError, get_ai_provider


def create_and_analyze_job(db: Session, user: User, data: JobCreate) -> Job:
    provider = get_ai_provider()
    try:
        result = provider.analyze_job(data.description_raw)
    except AIProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI job analysis failed: {exc}") from exc

    job = Job(
        user_id=user.id,
        title=data.title,
        company=data.company,
        description_raw=data.description_raw,
        extracted_data=result.model_dump(),
        job_url=data.job_url,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session, user: User) -> list[Job]:
    stmt = select(Job).where(Job.user_id == user.id).order_by(Job.created_at.desc())
    return list(db.scalars(stmt))


def get_job(db: Session, user: User, job_id: uuid.UUID) -> Job:
    job = db.get(Job, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


def delete_job(db: Session, user: User, job_id: uuid.UUID) -> None:
    job = get_job(db, user, job_id)
    db.delete(job)
    db.commit()
