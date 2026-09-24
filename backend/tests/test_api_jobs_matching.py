from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_JD = (FIXTURES / "sample_job_description.txt").read_text()


def _analyze_sample_job(client: TestClient, headers: dict):
    return client.post(
        "/api/jobs/analyze",
        headers=headers,
        json={"title": "Full Stack Developer", "company": "Acme Corp", "description_raw": SAMPLE_JD},
    )


def _upload_sample_resume(client: TestClient, headers: dict):
    with open(FIXTURES / "sample_resume.pdf", "rb") as f:
        return client.post(
            "/api/resumes/upload",
            headers=headers,
            files={"file": ("sample_resume.pdf", f, "application/pdf")},
        )


def test_analyze_job_extracts_skills(client: TestClient, auth_headers: dict):
    response = _analyze_sample_job(client, auth_headers)
    assert response.status_code == 201
    data = response.json()["extracted_data"]
    assert "React" in data["required_skills"]
    assert "AWS" in data["preferred_skills"]
    assert data["min_experience_years"] == 3


def test_analyze_job_requires_authentication(client: TestClient):
    response = client.post("/api/jobs/analyze", json={"title": "X", "description_raw": SAMPLE_JD})
    assert response.status_code == 401


def test_analyze_job_rejects_too_short_description(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/jobs/analyze", headers=auth_headers, json={"title": "X", "description_raw": "too short"}
    )
    assert response.status_code == 422


def test_list_and_delete_job(client: TestClient, auth_headers: dict):
    job_id = _analyze_sample_job(client, auth_headers).json()["id"]

    listed = client.get("/api/jobs", headers=auth_headers).json()
    assert any(j["id"] == job_id for j in listed)

    delete_response = client.delete(f"/api/jobs/{job_id}", headers=auth_headers)
    assert delete_response.status_code == 204
    assert client.get(f"/api/jobs/{job_id}", headers=auth_headers).status_code == 404


def test_matching_produces_score_and_skill_breakdown(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample_resume(client, auth_headers).json()["id"]
    job_id = _analyze_sample_job(client, auth_headers).json()["id"]

    response = client.post(
        "/api/matching/analyze", headers=auth_headers, json={"resume_id": resume_id, "job_id": job_id}
    )
    assert response.status_code == 201
    body = response.json()
    assert 0 <= body["match_score"] <= 100
    assert "Python" in body["matched_skills"]


def test_rerunning_match_updates_not_duplicates(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample_resume(client, auth_headers).json()["id"]
    job_id = _analyze_sample_job(client, auth_headers).json()["id"]

    first = client.post(
        "/api/matching/analyze", headers=auth_headers, json={"resume_id": resume_id, "job_id": job_id}
    ).json()
    second = client.post(
        "/api/matching/analyze", headers=auth_headers, json={"resume_id": resume_id, "job_id": job_id}
    ).json()

    assert first["id"] == second["id"]


def test_matching_against_another_users_job_returns_404(client: TestClient, auth_headers: dict):
    resume_id = _upload_sample_resume(client, auth_headers).json()["id"]

    client.post("/api/auth/register", json={"email": "jobowner@example.com", "password": "supersecret123"})
    owner_login = client.post(
        "/api/auth/login",
        data={"username": "jobowner@example.com", "password": "supersecret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}
    other_job_id = _analyze_sample_job(client, owner_headers).json()["id"]

    response = client.post(
        "/api/matching/analyze", headers=auth_headers, json={"resume_id": resume_id, "job_id": other_job_id}
    )
    assert response.status_code == 404
