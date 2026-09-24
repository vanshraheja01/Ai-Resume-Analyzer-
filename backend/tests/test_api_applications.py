from fastapi.testclient import TestClient


def _create_application(client: TestClient, headers: dict, **overrides):
    payload = {"company": "Acme Corp", "position_title": "Backend Engineer", "status": "saved"}
    payload.update(overrides)
    return client.post("/api/applications", headers=headers, json=payload)


def test_create_and_list_application(client: TestClient, auth_headers: dict):
    create_response = _create_application(client, auth_headers)
    assert create_response.status_code == 201
    assert create_response.json()["status"] == "saved"

    listed = client.get("/api/applications", headers=auth_headers).json()
    assert len(listed) == 1


def test_create_requires_authentication(client: TestClient):
    response = client.post(
        "/api/applications", json={"company": "Acme Corp", "position_title": "Backend Engineer"}
    )
    assert response.status_code == 401


def test_update_is_partial(client: TestClient, auth_headers: dict):
    app_id = _create_application(client, auth_headers, notes="Initial note").json()["id"]

    response = client.put(f"/api/applications/{app_id}", headers=auth_headers, json={"status": "interview"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interview"
    assert body["notes"] == "Initial note"
    assert body["company"] == "Acme Corp"


def test_filter_by_status(client: TestClient, auth_headers: dict):
    _create_application(client, auth_headers, company="A", status="saved")
    _create_application(client, auth_headers, company="B", status="applied")
    _create_application(client, auth_headers, company="C", status="applied")

    applied_only = client.get("/api/applications?status=applied", headers=auth_headers).json()
    assert len(applied_only) == 2
    assert all(a["status"] == "applied" for a in applied_only)


def test_delete_application(client: TestClient, auth_headers: dict):
    app_id = _create_application(client, auth_headers).json()["id"]
    delete_response = client.delete(f"/api/applications/{app_id}", headers=auth_headers)
    assert delete_response.status_code == 204
    assert client.get(f"/api/applications/{app_id}", headers=auth_headers).status_code == 404


def test_cannot_link_application_to_another_users_resume(client: TestClient, auth_headers: dict):
    from pathlib import Path

    client.post("/api/auth/register", json={"email": "resumeowner@example.com", "password": "supersecret123"})
    owner_login = client.post(
        "/api/auth/login",
        data={"username": "resumeowner@example.com", "password": "supersecret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    fixtures = Path(__file__).parent / "fixtures"
    with open(fixtures / "sample_resume.pdf", "rb") as f:
        other_resume = client.post(
            "/api/resumes/upload",
            headers=owner_headers,
            files={"file": ("sample_resume.pdf", f, "application/pdf")},
        )
    assert other_resume.status_code == 201
    other_resume_id = other_resume.json()["id"]

    response = _create_application(client, auth_headers, resume_id=other_resume_id)
    assert response.status_code == 404


def test_dashboard_aggregates_correctly(client: TestClient, auth_headers: dict):
    _create_application(client, auth_headers, company="A", status="applied")
    _create_application(client, auth_headers, company="B", status="interview")
    _create_application(client, auth_headers, company="C", status="technical_round")
    _create_application(client, auth_headers, company="D", status="offer")

    stats = client.get("/api/dashboard", headers=auth_headers).json()
    assert stats["total_applications"] == 4
    assert stats["interviews"] == 2
    assert stats["offers"] == 1
    assert stats["pending"] == 1
    assert stats["by_status"]["saved"] == 0
