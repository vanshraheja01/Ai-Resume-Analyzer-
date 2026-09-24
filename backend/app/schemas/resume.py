import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResumeSummary(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    file_type: str
    file_size: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ResumeDetail(ResumeSummary):
    parsed_data: dict[str, Any] | None
    raw_text: str | None


class ResumeAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    overall_score: int
    skills_score: int
    experience_score: int
    projects_score: int
    education_score: int
    structure_score: int
    job_relevance_score: int
    achievements_score: int
    keywords_score: int
    strengths: list[str] | None
    weaknesses: list[str] | None
    recommendations: list[str] | None
    ai_provider_used: str | None
    created_at: datetime
