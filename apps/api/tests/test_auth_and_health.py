from fastapi.testclient import TestClient


def test_health_and_readiness_are_available(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/ready").json() == {"ok": True, "database": "ready"}


def test_protected_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401


def test_login_rejects_wrong_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "mezie", "password": "incorrect"},
    )
    assert response.status_code == 401
