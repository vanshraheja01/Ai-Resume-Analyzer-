from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.match import Match
from app.models.user import User
from app.schemas.matching import MatchRequest, MatchResponse
from app.services import auth_service, matching_service

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/analyze", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def analyze_match(
    data: MatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Match:
    return matching_service.match_resume_to_job(db, current_user, data.resume_id, data.job_id)
