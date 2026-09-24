import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.user import User
from app.services import job_service, resume_service
from app.services.ai_service import AIProviderError, get_ai_provider


def match_resume_to_job(db: Session, user: User, resume_id: uuid.UUID, job_id: uuid.UUID) -> Match:

    resume = resume_service.get_resume(db, user, resume_id)
    job = job_service.get_job(db, user, job_id)

    provider = get_ai_provider()
    try:
        result = provider.match_resume_job(resume.parsed_data or {}, job.extracted_data or {})
    except AIProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI matching failed: {exc}") from exc

    existing = db.scalar(select(Match).where(Match.resume_id == resume.id, Match.job_id == job.id))
    match = existing or Match(resume_id=resume.id, job_id=job.id)

    match.match_score = result.match_score
    match.matched_skills = result.matched_skills
    match.missing_skills = result.missing_skills
    match.partial_skills = result.partial_skills
    match.recommendations = result.recommendations

    if existing is None:
        db.add(match)
    db.commit()
    db.refresh(match)
    return match
