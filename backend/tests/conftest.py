import os
import shutil
import tempfile

os.environ["DATABASE_URL"] = "postgresql+psycopg://resume_user:resume_pass@localhost:5432/resume_analyzer_test"
os.environ["AI_MODE"] = "mock"

_TEST_STORAGE_DIR = tempfile.mkdtemp(prefix="resume_analyzer_test_storage_")
os.environ["LOCAL_STORAGE_PATH"] = _TEST_STORAGE_DIR

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

get_settings.cache_clear()
settings = get_settings()

from app import models
from app.database.base import Base
from app.database.connection import get_db
from app.main import app

engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree(_TEST_STORAGE_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient):
    email = "fixture-user@example.com"
    password = "testpass123"
    client.post("/api/auth/register", json={"email": email, "password": password, "full_name": "Fixture User"})
    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
