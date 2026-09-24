import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResumeSummary(BaseModel):
    """Lightweight shape for list views — leaves out raw_text/parsed_data."""

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
