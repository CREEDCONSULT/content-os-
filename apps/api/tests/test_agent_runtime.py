from __future__ import annotations

from fastapi.testclient import TestClient


def test_skill_registry_is_seeded_from_supplied_contracts(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/agent/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) == 30
    router = next(item for item in skills if item["slug"] == "00_skill_router")
    assert router["version"] == "1.0.0"
    assert "Database" in router["allowed_tools"]
    assert router["output_schema"]["type"] == "object"


def test_mock_run_routes_skills_and_records_context(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post(
        "/api/v1/agent/runs",
        json={
            "channel": "dashboard",
            "intent": "Draft a script and three hooks about building BrandOS in public",
            "raw_input": {"platform": "LinkedIn"},
            "idempotency_key": "test-script-run-0001",
        },
    )
    assert response.status_code == 201
    run = response.json()
    assert run["status"] == "completed"
    assert run["provider"] == "mock"
    assert "08_scriptwriting" in run["skills_used"]
    assert "09_hook_lab" in run["skills_used"]
    assert run["context_pack_id"]
    assert run["context_loaded"]
    assert run["completed_writes"] == []
    assert run["output_envelope"]["status"] == "success"
    classifications = run["output_envelope"]["outputs"]["provider_output"]["classifications"]
    assert {item["type"] for item in classifications} == {
        "verified_fact",
        "model_inference",
    }

    context_response = authenticated_client.get(
        f"/api/v1/agent/context-packs/{run['context_pack_id']}"
    )
    assert context_response.status_code == 200
    context = context_response.json()
    assert context["source_records"]
    assert context["token_estimate"] > 0
    assert all(item["authority"] == "canonical" for item in context["source_records"])


def test_agent_run_idempotency_returns_original_run(
    authenticated_client: TestClient,
) -> None:
    payload = {
        "intent": "Review an internal content idea",
        "idempotency_key": "test-idempotent-run-0001",
    }
    first = authenticated_client.post("/api/v1/agent/runs", json=payload)
    second = authenticated_client.post("/api/v1/agent/runs", json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_budget_and_public_action_create_backend_approval(
    authenticated_client: TestClient,
) -> None:
    budget_response = authenticated_client.post(
        "/api/v1/agent/runs",
        json={
            "intent": "Research current creator patterns",
            "budget": {"model_usd": 2, "tool_usd": 0},
        },
    )
    assert budget_response.status_code == 201
    budget_run = budget_response.json()
    assert budget_run["status"] == "blocked"
    assert budget_run["approvals_required"][0]["action_type"] == "paid_tool_use_above_budget"

    publish_response = authenticated_client.post(
        "/api/v1/agent/runs",
        json={"intent": "Publish this content publicly now"},
    )
    assert publish_response.status_code == 201
    publish_run = publish_response.json()
    assert publish_run["status"] == "blocked"
    assert publish_run["approvals_required"][0]["action_type"] == "public_publishing"

    approvals = authenticated_client.get("/api/v1/approvals?status=pending")
    assert approvals.status_code == 200
    assert len(approvals.json()) == 2
