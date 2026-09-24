import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    position_title: str = Field(min_length=1, max_length=255)
    status: ApplicationStatus = ApplicationStatus.SAVED
    job_id: uuid.UUID | None = None
    resume_id: uuid.UUID | None = None
    application_date: date | None = None
    interview_date: date | None = None
    job_url: str | None = Field(default=None, max_length=1000)
    notes: str | None = None


class ApplicationUpdate(BaseModel):

    company: str | None = Field(default=None, min_length=1, max_length=255)
    position_title: str | None = Field(default=None, min_length=1, max_length=255)
    status: ApplicationStatus | None = None
    job_id: uuid.UUID | None = None
    resume_id: uuid.UUID | None = None
    application_date: date | None = None
    interview_date: date | None = None
    job_url: str | None = Field(default=None, max_length=1000)
    notes: str | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company: str
    position_title: str
    status: ApplicationStatus
    job_id: uuid.UUID | None
    resume_id: uuid.UUID | None
    application_date: date | None
    interview_date: date | None
    job_url: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
