import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path

from app.config import get_settings


class StorageBackend(ABC):
    @abstractmethod
    def save(self, content: bytes, original_filename: str) -> str:
        pass

    @abstractmethod
    def get_path(self, key: str) -> Path:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass


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

    raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.storage_backend}")
