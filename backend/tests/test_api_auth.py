from fastapi.testclient import TestClient


def test_register_returns_user_without_password(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "supersecret123", "full_name": "New User"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert body["full_name"] == "New User"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_rejected(client: TestClient):
    payload = {"email": "dup@example.com", "password": "supersecret123"}
    first = client.post("/api/auth/register", json=payload)
    second = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 400


def test_register_rejects_short_password(client: TestClient):
    response = client.post("/api/auth/register", json={"email": "short@example.com", "password": "short"})
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client: TestClient):
    client.post("/api/auth/register", json={"email": "loginuser@example.com", "password": "supersecret123"})
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser@example.com", "password": "supersecret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_fails_with_wrong_password(client: TestClient):
    client.post("/api/auth/register", json={"email": "wrongpass@example.com", "password": "supersecret123"})
    response = client.post(
        "/api/auth/login",
        data={"username": "wrongpass@example.com", "password": "incorrect"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_login_fails_for_unknown_email(client: TestClient):
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "whatever123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient, auth_headers: dict):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "fixture-user@example.com"


def test_me_rejects_garbage_token(client: TestClient):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_update_profile_persists_fields(client: TestClient, auth_headers: dict):
    response = client.put(
        "/api/auth/me",
        headers=auth_headers,
        json={
            "full_name": "Updated Name",
            "location": "Remote",
            "github_url": "https://github.com/someone",
            "preferred_role": "Backend Engineer",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Updated Name"
    assert body["location"] == "Remote"
    assert body["preferred_role"] == "Backend Engineer"

    # Confirm it actually persisted, not just echoed back.
    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.json()["location"] == "Remote"
