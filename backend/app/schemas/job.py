import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    description_raw: str = Field(min_length=20)
    job_url: str | None = Field(default=None, max_length=1000)


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None
    description_raw: str
    extracted_data: dict[str, Any] | None
    job_url: str | None
    created_at: datetime
