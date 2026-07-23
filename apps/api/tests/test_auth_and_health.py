from fastapi.testclient import TestClient

from app.routers.auth import _clear_failures


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


def test_login_cookie_and_security_headers(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "mezie", "password": "brandos-local-dev"},
    )

    assert response.status_code == 200
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]


def test_login_attempts_are_bounded(client: TestClient) -> None:
    try:
        for _ in range(8):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "mezie", "password": "incorrect"},
            )
            assert response.status_code == 401

        blocked = client.post(
            "/api/v1/auth/login",
            json={"username": "mezie", "password": "incorrect"},
        )
        assert blocked.status_code == 429
        assert blocked.headers["retry-after"] == "300"
    finally:
        _clear_failures("testclient")
