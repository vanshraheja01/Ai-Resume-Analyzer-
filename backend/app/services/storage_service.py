"""Storage abstraction for uploaded files.

Every route/service talks to `StorageBackend`, never to the filesystem (or,
later, S3/Supabase Storage) directly. `Resume.file_path` stores whatever
opaque key the active backend hands back — swapping backends later means
adding one class here and changing `get_storage_backend()`, nothing else.
"""

import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path

from app.config import get_settings


class StorageBackend(ABC):
    @abstractmethod
    def save(self, content: bytes, original_filename: str) -> str:
        """Persist file content, returning an opaque key to retrieve it later."""

    @abstractmethod
    def get_path(self, key: str) -> Path:
        """Return a local filesystem path the file's bytes can be read from."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove the stored file. Must not raise if it's already gone."""


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, original_filename: str) -> str:
        extension = Path(original_filename).suffix.lower()
        key = f"{uuid.uuid4()}{extension}"
        (self._base_dir / key).write_bytes(content)
        return key

    def get_path(self, key: str) -> Path:
        return self._base_dir / key

    def delete(self, key: str) -> None:
        path = self.get_path(key)
        path.unlink(missing_ok=True)


@lru_cache
def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "local":
        return LocalStorageBackend(settings.local_storage_path)
    # Future: elif settings.storage_backend == "s3": return S3StorageBackend(...)
    raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")
