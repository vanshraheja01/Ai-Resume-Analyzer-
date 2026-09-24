import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse
from app.services import auth_service, job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def analyze_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Job:
    return job_service.create_and_analyze_job(db, current_user, data)


@router.get("", response_model=list[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[Job]:
    return job_service.list_jobs(db, current_user)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Job:
    return job_service.get_job(db, current_user, job_id)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    job_service.delete_job(db, current_user, job_id)
