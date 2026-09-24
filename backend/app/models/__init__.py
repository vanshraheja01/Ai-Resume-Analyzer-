"""Import every model here so Base.metadata is fully populated for Alembic
autogenerate and so relationship() string references resolve correctly."""

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.match import Match
from app.models.resume import Resume, ResumeAnalysis
from app.models.user import User

__all__ = [
    "User",
    "Resume",
    "ResumeAnalysis",
    "Job",
    "Match",
    "Application",
    "ApplicationStatus",
]
