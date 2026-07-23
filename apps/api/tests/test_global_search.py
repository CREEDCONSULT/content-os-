from __future__ import annotations

from fastapi.testclient import TestClient


def test_global_search_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "builder"})
    assert response.status_code == 401


def test_global_search_returns_ranked_workspace_records(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get(
        "/api/v1/search",
        params={"q": "builder"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(
        {
            "id",
            "record_type",
            "title",
            "excerpt",
            "href",
            "authority",
            "score",
            "is_demo",
        }
        <= result.keys()
        for result in payload
    )
    assert [result["score"] for result in payload] == sorted(
        [result["score"] for result in payload],
        reverse=True,
    )


def test_global_search_rejects_single_character_query(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/search", params={"q": "x"})
    assert response.status_code == 422
