import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    match_score: int
    matched_skills: list[str] | None
    missing_skills: list[str] | None
    partial_skills: list[str] | None
    recommendations: list[str] | None
    created_at: datetime
