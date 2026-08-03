from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.db.models import AgentRun, Brand
from app.services.actions import create_actions_from_agent_run
from app.services.providers import OpenAIResponsesProvider


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


def test_dashboard_conversation_turn_records_messages_and_agent_run(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post(
        "/api/v1/conversations/messages",
        json={
            "channel": "dashboard",
            "content_text": "Help me brainstorm a 30 day BrandOS content sprint.",
        },
    )
    assert response.status_code == 201
    turn = response.json()
    assert turn["session"]["channel"] == "dashboard"
    assert turn["user_message"]["sender_type"] == "user"
    assert turn["agent_message"]["sender_type"] == "agent"
    assert turn["agent_run"]["status"] == "completed"
    assert turn["reply_text"]

    sessions = authenticated_client.get("/api/v1/conversations")
    assert sessions.status_code == 200
    assert sessions.json()["total"] >= 1

    messages = authenticated_client.get(
        f"/api/v1/conversations/{turn['session']['id']}/messages"
    )
    assert messages.status_code == 200
    assert {item["sender_type"] for item in messages.json()} >= {"user", "agent"}


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


def test_safe_dashboard_action_executes_as_tracked_tool_call(
    authenticated_client: TestClient,
) -> None:
    proposal = authenticated_client.post(
        "/api/v1/actions/proposals",
        json={
            "action_type": "create_rough_idea",
            "payload": {
                "title": "Agentic rough-work command center",
                "raw_input": (
                    "Turn Telegram brainstorming into a governed dashboard proposal queue."
                ),
                "source_type": "dashboard_agent",
                "platform_fit": ["LinkedIn"],
            },
            "rationale": "This is an internal rough idea and does not publish externally.",
            "risk_level": "low",
        },
    )
    assert proposal.status_code == 201
    action = proposal.json()
    assert action["status"] == "proposed"
    assert action["risk_level"] == "low"

    executed = authenticated_client.post(
        f"/api/v1/actions/proposals/{action['id']}/execute"
    )
    assert executed.status_code == 200
    result = executed.json()
    assert result["action"]["status"] == "executed"
    assert result["action"]["target_type"] == "idea"
    assert result["tool_call"]["tool_name"] == "create_rough_idea"
    assert result["tool_call"]["tool_type"] == "safe_write"
    assert result["tool_call"]["status"] == "completed"

    ideas = authenticated_client.get(
        "/api/v1/ideas",
        params={"search": "Agentic rough-work command center"},
    )
    assert ideas.status_code == 200
    assert ideas.json()["total"] == 1
    assert ideas.json()["items"][0]["source_type"] == "dashboard_agent"

    tool_calls = authenticated_client.get("/api/v1/actions/tool-calls")
    assert tool_calls.status_code == 200
    assert tool_calls.json()[0]["status"] == "completed"


def test_risky_dashboard_action_requires_approval_instead_of_executing(
    authenticated_client: TestClient,
) -> None:
    proposal = authenticated_client.post(
        "/api/v1/actions/proposals",
        json={
            "action_type": "publish_content",
            "target_type": "content_item",
            "target_id": "00000000-0000-0000-0000-000000000001",
            "payload": {"platform": "LinkedIn", "caption": "Ship it publicly."},
            "rationale": "Publishing affects the public brand surface.",
            "risk_level": "low",
        },
    )
    assert proposal.status_code == 201
    action = proposal.json()
    assert action["risk_level"] == "high"

    blocked = authenticated_client.post(
        f"/api/v1/actions/proposals/{action['id']}/execute"
    )
    assert blocked.status_code == 200
    result = blocked.json()
    assert result["action"]["status"] == "approval_required"
    assert result["action"]["approval_id"]
    assert result["tool_call"]["status"] == "blocked"
    assert result["tool_call"]["approval_id"] == result["action"]["approval_id"]

    approvals = authenticated_client.get("/api/v1/approvals?status=pending")
    assert approvals.status_code == 200
    approval = next(
        item
        for item in approvals.json()
        if item["target_type"] == "proposed_dashboard_action"
    )
    assert approval["action_type"] == "publish_content"
    assert approval["risk_level"] == "high"


def test_agent_proposed_write_becomes_dashboard_action(db: Session) -> None:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    assert brand is not None
    run = AgentRun(
        brand_id=brand.id,
        channel="dashboard",
        intent="Brainstorm a safe internal idea",
        status="completed",
        provider="mock",
        model_alias="mock_brand_fast_model",
        input_envelope={
            "raw_input": {
                "channel": "dashboard",
                "content_text": "A rough idea about the agentic content command room.",
            }
        },
        summary="The rough idea is worth saving as an internal draft.",
        proposed_writes=[
            {
                "record_type": "idea",
                "action": "create_rough_idea",
                "rationale": "It belongs in the Ideas Inbox for later scoring.",
            }
        ],
        is_demo=True,
    )
    db.add(run)
    db.flush()

    created = create_actions_from_agent_run(
        db,
        run,
        UserPrincipal(
            username="test-agent",
            display_name="Test Agent",
            permissions=("read", "draft", "internal_write"),
        ),
        session_id=None,
    )
    db.commit()

    assert len(created) == 1
    assert created[0].action_type == "create_rough_idea"
    assert created[0].status == "proposed"
    assert created[0].payload["title"] == "A rough idea about the agentic content command room."
    assert created[0].payload["source_reference"] == f"agent_run:{run.id}"


def test_openai_strict_schema_defines_proposed_writes_items() -> None:
    schema = OpenAIResponsesProvider._output_schema()
    proposed_writes = schema["properties"]["proposed_writes"]["items"]
    assert proposed_writes["additionalProperties"] is False
    assert proposed_writes["required"] == ["record_type", "action", "rationale"]
