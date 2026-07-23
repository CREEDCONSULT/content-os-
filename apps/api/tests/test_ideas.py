from fastapi.testclient import TestClient


def test_create_and_score_idea(authenticated_client: TestClient) -> None:
    created = authenticated_client.post(
        "/api/v1/ideas",
        json={
            "title": "A founder needs an operating rhythm",
            "raw_input": "Explain the weekly system that survives low motivation.",
            "pillar": "Lead",
            "series": "Builder Walks",
            "platform_fit": ["Instagram", "LinkedIn", "Instagram"],
        },
    )
    assert created.status_code == 201
    idea = created.json()
    assert idea["is_demo"] is False
    assert idea["platform_fit"] == ["Instagram", "LinkedIn"]

    scored = authenticated_client.post(
        f"/api/v1/ideas/{idea['id']}/score",
        json={
            "brand_fit_score": 9,
            "audience_value_score": 8,
            "proof_score": 7,
            "timeliness_score": 8,
            "originality_score": 8,
            "feasibility_score": 9,
            "strategic_importance_score": 9,
        },
    )
    assert scored.status_code == 200
    assert scored.json()["total_priority_score"] == 8.3


def test_rejected_idea_requires_reason(authenticated_client: TestClient) -> None:
    ideas = authenticated_client.get("/api/v1/ideas").json()["items"]
    response = authenticated_client.patch(
        f"/api/v1/ideas/{ideas[0]['id']}",
        json={"status": "rejected"},
    )
    assert response.status_code == 422
