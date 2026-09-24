import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.resume import Resume
from app.models.user import User
from app.services import resume_parser
from app.services.storage_service import get_storage_backend

ALLOWED_EXTENSIONS = {".pdf": "pdf", ".docx": "docx"}


def _validate_upload(filename: str | None, content: bytes) -> str:
    settings = get_settings()
    extension = Path(filename or "").suffix.lower()
    file_type = ALLOWED_EXTENSIONS.get(extension)
    if file_type is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF and DOCX files are supported")

    if len(content) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file is empty")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File exceeds the {settings.max_upload_size_mb}MB upload limit",
        )

    return file_type


def upload_resume(db: Session, user: User, file: UploadFile, title: str | None) -> Resume:
    content = file.file.read()
    file_type = _validate_upload(file.filename, content)

    storage = get_storage_backend()
    key = storage.save(content, file.filename or f"resume.{file_type}")

    try:
        raw_text = resume_parser.extract_text(storage.get_path(key), file_type)
        parsed_data = resume_parser.parse_resume(raw_text)
    except resume_parser.ResumeParsingError as exc:
        try:
            storage.delete(key)
        except OSError:
            # Best-effort cleanup: on Windows, a library that failed to parse a
            # corrupted file may still hold its handle open briefly. The orphaned
            # file is harmless — it's never referenced by any DB row.
            pass
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    resume = Resume(
        user_id=user.id,
        title=title or (file.filename or "Untitled Resume"),
        file_path=key,
        file_type=file_type,
        file_size=len(content),
        raw_text=raw_text,
        parsed_data=parsed_data,
        is_active=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session, user: User) -> list[Resume]:
    stmt = select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    return list(db.scalars(stmt))


def get_resume(db: Session, user: User, resume_id: uuid.UUID) -> Resume:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return resume


def delete_resume(db: Session, user: User, resume_id: uuid.UUID) -> None:
    resume = get_resume(db, user, resume_id)
    get_storage_backend().delete(resume.file_path)
    db.delete(resume)
    db.commit()
