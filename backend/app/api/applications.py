import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.services import application_service, auth_service

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> list[Application]:
    return application_service.list_applications(db, current_user, status_filter)


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Application:
    return application_service.create_application(db, current_user, data)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Application:
    return application_service.get_application(db, current_user, application_id)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Application:
    return application_service.update_application(db, current_user, application_id, data)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    application_service.delete_application(db, current_user, application_id)
