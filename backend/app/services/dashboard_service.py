from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.dashboard import DashboardStats


def get_dashboard_stats(db: Session, user: User) -> DashboardStats:
    applications = list(db.scalars(select(Application).where(Application.user_id == user.id)))
    counts = Counter(app.status for app in applications)
    by_status = {s.value: counts.get(s, 0) for s in ApplicationStatus}

    total_resumes = db.scalar(select(func.count()).select_from(Resume).where(Resume.user_id == user.id)) or 0
    total_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.user_id == user.id)) or 0

    return DashboardStats(
        total_applications=len(applications),
        by_status=by_status,
        interviews=by_status[ApplicationStatus.INTERVIEW.value] + by_status[ApplicationStatus.TECHNICAL_ROUND.value],
        offers=by_status[ApplicationStatus.OFFER.value],
        pending=by_status[ApplicationStatus.APPLIED.value],
        total_resumes=total_resumes,
        total_jobs_analyzed=total_jobs,
    )
