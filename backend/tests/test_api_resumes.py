from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent / "fixtures"


def _upload_sample(client: TestClient, headers: dict, filename: str = "sample_resume.pdf"):
    with open(FIXTURES / filename, "rb") as f:
        return client.post(
            "/api/resumes/upload",
            headers=headers,
            files={"file": (filename, f, "application/octet-stream")},
        )


def test_upload_pdf_resume_parses_correctly(client: TestClient, auth_headers: dict):
    response = _upload_sample(client, auth_headers, "sample_resume.pdf")
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "pdf"
    assert body["parsed_data"]["email"] == "priya.sharma@example.com"
    assert "Python" in body["parsed_data"]["skills"]


def test_upload_docx_resume_parses_correctly(client: TestClient, auth_headers: dict):
    response = _upload_sample(client, auth_headers, "sample_resume.docx")
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "docx"
    assert body["parsed_data"]["name"] == "Priya Sharma"


def test_upload_requires_authentication(client: TestClient):
    with open(FIXTURES / "sample_resume.pdf", "rb") as f:
        response = client.post("/api/resumes/upload", files={"file": ("sample_resume.pdf", f, "application/pdf")})
    assert response.status_code == 401


def test_upload_rejects_unsupported_file_type(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/resumes/upload",
        headers=auth_headers,
        files={"file": ("notes.txt", b"just some text", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_corrupted_pdf(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/resumes/upload",
        headers=auth_headers,
        files={"file": ("broken.pdf", b"not a real pdf", "application/pdf")},
    )
    assert response.status_code == 422


def test_list_resumes_only_returns_own(client: TestClient, auth_headers: dict):
    _upload_sample(client, auth_headers)
    client.post("/api/auth/register", json={"email": "otheruser@example.com", "password": "supersecret123"})
    other_login = client.post(
        "/api/auth/login",
        data={"username": "otheruser@example.com", "password": "supersecret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    mine = client.get("/api/resumes", headers=auth_headers).json()
    theirs = client.get("/api/resumes", headers=other_headers).json()
    assert len(mine) == 1
    assert len(theirs) == 0


def test_get_another_users_resume_returns_404(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample(client, auth_headers).json()["id"]

    client.post("/api/auth/register", json={"email": "otheruser2@example.com", "password": "supersecret123"})
    other_login = client.post(
        "/api/auth/login",
        data={"username": "otheruser2@example.com", "password": "supersecret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.get(f"/api/resumes/{resume_id}", headers=other_headers)
    assert response.status_code == 404


def test_delete_resume_removes_it(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample(client, auth_headers).json()["id"]
    delete_response = client.delete(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_analyze_resume_returns_valid_scores(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample(client, auth_headers).json()["id"]
    response = client.post(f"/api/resumes/{resume_id}/analyze", headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert 0 <= body["overall_score"] <= 100
    assert body["ai_provider_used"] == "mock"


def test_analyze_history_accumulates(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample(client, auth_headers).json()["id"]
    client.post(f"/api/resumes/{resume_id}/analyze", headers=auth_headers)
    client.post(f"/api/resumes/{resume_id}/analyze", headers=auth_headers)

    history = client.get(f"/api/resumes/{resume_id}/analyses", headers=auth_headers).json()
    assert len(history) == 2
