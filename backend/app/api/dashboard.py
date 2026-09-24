from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services import auth_service, dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> DashboardStats:
    return dashboard_service.get_dashboard_stats(db, current_user)
