from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, sourced from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AI Resume Analyzer API"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+psycopg://resume_user:resume_pass@localhost:5432/resume_analyzer"

    # Auth
    jwt_secret_key: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Storage
    storage_backend: str = "local"
    local_storage_path: str = "./storage/uploads"
    max_upload_size_mb: int = 5

    # AI
    ai_mode: str = "mock"  # "mock" | "live"
    ai_provider: str = "gemini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
