from fastapi.testclient import TestClient


def test_invalid_pipeline_transition_is_rejected(authenticated_client: TestClient) -> None:
    items = authenticated_client.get("/api/v1/content").json()["items"]
    item = next(candidate for candidate in items if candidate["status"] == "research")
    response = authenticated_client.post(
        f"/api/v1/content/{item['id']}/transition",
        json={"to_status": "published", "reason": "Skip all gates"},
    )
    assert response.status_code == 409


def test_publish_transition_requires_backend_approval(authenticated_client: TestClient) -> None:
    items = authenticated_client.get("/api/v1/content").json()["items"]
    item = next(candidate for candidate in items if candidate["status"] == "review")

    transitions = [
        "approved",
        "ready_to_shoot",
        "shot",
        "editing",
        "review_edit",
        "ready_to_publish",
    ]
    for target in transitions:
        response = authenticated_client.post(
            f"/api/v1/content/{item['id']}/transition",
            json={"to_status": target, "reason": "Advance test workflow"},
        )
        assert response.status_code == 200

    blocked = authenticated_client.post(
        f"/api/v1/content/{item['id']}/transition",
        json={"to_status": "published", "reason": "Attempt without approval"},
    )
    assert blocked.status_code == 403
