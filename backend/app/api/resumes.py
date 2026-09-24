import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.resume import Resume, ResumeAnalysis
from app.models.user import User
from app.schemas.resume import ResumeAnalysisResponse, ResumeDetail, ResumeSummary
from app.services import auth_service, resume_service

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Resume:
    return resume_service.upload_resume(db, current_user, file, title)


@router.get("", response_model=list[ResumeSummary])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[Resume]:
    return resume_service.list_resumes(db, current_user)


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Resume:
    return resume_service.get_resume(db, current_user, resume_id)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    resume_service.delete_resume(db, current_user, resume_id)


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> ResumeAnalysis:
    resume = resume_service.get_resume(db, current_user, resume_id)
    return resume_service.analyze_resume(db, resume)


@router.get("/{resume_id}/analyses", response_model=list[ResumeAnalysisResponse])
def list_resume_analyses(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[ResumeAnalysis]:
    resume = resume_service.get_resume(db, current_user, resume_id)
    return resume_service.list_analyses(db, resume)
