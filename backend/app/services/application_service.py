import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.services import job_service, resume_service


def _validate_linked_ids(db: Session, user: User, job_id: uuid.UUID | None, resume_id: uuid.UUID | None) -> None:
    # Reuses the existing ownership-checked getters so a user can never link
    # an application to another user's job or resume.
    if job_id is not None:
        job_service.get_job(db, user, job_id)
    if resume_id is not None:
        resume_service.get_resume(db, user, resume_id)


def create_application(db: Session, user: User, data: ApplicationCreate) -> Application:
    _validate_linked_ids(db, user, data.job_id, data.resume_id)

    application = Application(user_id=user.id, **data.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_applications(
    db: Session, user: User, status_filter: ApplicationStatus | None = None
) -> list[Application]:
    stmt = select(Application).where(Application.user_id == user.id)
    if status_filter is not None:
        stmt = stmt.where(Application.status == status_filter)
    stmt = stmt.order_by(Application.created_at.desc())
    return list(db.scalars(stmt))


def get_application(db: Session, user: User, application_id: uuid.UUID) -> Application:
    application = db.get(Application, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return application


def update_application(
    db: Session, user: User, application_id: uuid.UUID, data: ApplicationUpdate
) -> Application:
    application = get_application(db, user, application_id)
    updates = data.model_dump(exclude_unset=True)

    _validate_linked_ids(db, user, updates.get("job_id"), updates.get("resume_id"))

    for field, value in updates.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, user: User, application_id: uuid.UUID) -> None:
    application = get_application(db, user, application_id)
    db.delete(application)
    db.commit()
