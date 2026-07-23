from __future__ import annotations

from fastapi.testclient import TestClient


def _create_idea(client: TestClient, title: str, raw_input: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/ideas",
        json={
            "title": title,
            "raw_input": raw_input,
            "pillar": "Build",
            "audience": "Emerging Builder",
            "platform_fit": ["LinkedIn"],
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_script(
    client: TestClient,
    title: str,
    body_text: str,
    hook: str,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    idea = _create_idea(client, title, f"{body_text} Build a useful explanation.")
    brief_response = client.post(
        f"/api/v1/studio/briefs/from-idea/{idea['id']}",
        json={"platform": "LinkedIn", "format": "Post"},
    )
    assert brief_response.status_code == 201
    brief = brief_response.json()
    script_response = client.post(
        f"/api/v1/studio/briefs/{brief['id']}/scripts",
        json={
            "body_text": body_text,
            "hook_selected": hook,
            "hook_variants": [f"{hook} A second angle."],
            "cta": "What system will you build next?",
            "duration_seconds": 60,
            "brand_alignment_score": 9.1,
            "originality_score": 8.7,
            "change_summary": "Create test script",
        },
    )
    assert script_response.status_code == 201
    return idea, brief, script_response.json()


def test_idea_to_approved_script_and_production_gate(
    authenticated_client: TestClient,
) -> None:
    _, brief, script = _create_script(
        authenticated_client,
        "A system for founder consistency",
        (
            "Consistency improves when the next action is visible, the evidence is linked, "
            "and the review boundary is explicit."
        ),
        "Consistency is not motivation. It is system design.",
    )
    assert script["version_count"] == 1
    assert len(script["hooks"]) == 2
    assert script["status"] == "draft"

    fact_check = authenticated_client.post(
        f"/api/v1/studio/scripts/{script['id']}/fact-check",
        json={
            "claim_table": [],
            "sources": [],
            "unresolved_claims": [],
            "verified_text": script["current_version"]["body_text"],
            "confidence": 0.95,
        },
    )
    assert fact_check.status_code == 200
    assert fact_check.json()["status"] == "verified"
    refreshed_brief = authenticated_client.get(f"/api/v1/studio/briefs/{brief['id']}").json()
    assert refreshed_brief["evidence_status"] == "verified"

    submitted = authenticated_client.post(f"/api/v1/studio/scripts/{script['id']}/submit")
    assert submitted.status_code == 200
    submission = submitted.json()
    assert submission["script"]["status"] == "review"
    approval_id = submission["approval_id"]

    content_id = submission["script"]["content_item_id"]
    blocked = authenticated_client.post(
        f"/api/v1/content/{content_id}/transition",
        json={"to_status": "approved"},
    )
    assert blocked.status_code == 403

    approved = authenticated_client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={"decision": "approved", "notes": "Safe internal script approved."},
    )
    assert approved.status_code == 200
    detail = authenticated_client.get(f"/api/v1/studio/scripts/{script['id']}").json()
    assert detail["status"] == "approved"
    assert detail["approval_status"] == "approved"

    content = authenticated_client.get(f"/api/v1/content/{content_id}").json()
    assert content["status"] == "approved"
    ready = authenticated_client.post(
        f"/api/v1/content/{content_id}/transition",
        json={"to_status": "ready_to_shoot"},
    )
    assert ready.status_code == 403
    assert "production plan" in ready.json()["detail"].lower()


def test_financial_signal_is_blocked_and_new_version_resets_review(
    authenticated_client: TestClient,
) -> None:
    _, _, script = _create_script(
        authenticated_client,
        "A risky crypto draft",
        (
            "Buy this crypto now for guaranteed returns and double your money before "
            "the market notices."
        ),
        "This token will change everything.",
    )
    blocked_check = authenticated_client.post(
        f"/api/v1/studio/scripts/{script['id']}/fact-check",
        json={
            "claim_table": [{"claim": "Guaranteed returns", "risk": "critical"}],
            "sources": [{"url": "https://example.test/source", "type": "test"}],
            "unresolved_claims": [],
            "verified_text": script["current_version"]["body_text"],
            "confidence": 0.2,
        },
    )
    assert blocked_check.status_code == 200
    blocked = blocked_check.json()
    assert blocked["status"] == "blocked"
    assert "guaranteed return" in blocked["blocked_claims"]
    assert "direct buy signal" in blocked["blocked_claims"]

    rejected_submit = authenticated_client.post(f"/api/v1/studio/scripts/{script['id']}/submit")
    assert rejected_submit.status_code == 409

    revised = authenticated_client.post(
        f"/api/v1/studio/scripts/{script['id']}/versions",
        json={
            "body_text": (
                "An ETF can diversify exposure, but fees, composition, volatility, and "
                "personal circumstances still matter. Research the structure and risks."
            ),
            "hook_selected": "An ETF is a container, not a shortcut.",
            "hook_variants": ["Before you compare returns, inspect what the ETF owns."],
            "cta": "Which part of an ETF would you research first?",
            "duration_seconds": 55,
            "brand_alignment_score": 9,
            "originality_score": 9,
            "change_summary": "Remove prohibited signal language",
        },
    )
    assert revised.status_code == 201
    assert revised.json()["version_count"] == 2
    assert revised.json()["fact_check_status"] == "needs_review"

    safe_check = authenticated_client.post(
        f"/api/v1/studio/scripts/{script['id']}/fact-check",
        json={
            "claim_table": [],
            "sources": [],
            "unresolved_claims": [],
            "verified_text": revised.json()["current_version"]["body_text"],
            "confidence": 0.9,
        },
    )
    assert safe_check.status_code == 200
    safe = safe_check.json()
    assert safe["status"] == "verified"
    assert safe["financial_classification"] == "educational_financial_content"
    assert safe["risk_disclosures"]

    versions = authenticated_client.get(f"/api/v1/studio/scripts/{script['id']}/versions").json()
    assert [item["version_number"] for item in versions] == [2, 1]
    assert versions[0]["is_active"] is True
    assert versions[1]["is_active"] is False


def test_script_input_validation_rejects_empty_draft(
    authenticated_client: TestClient,
) -> None:
    idea = _create_idea(
        authenticated_client,
        "Short invalid script",
        "This idea has enough detail to become a brief.",
    )
    brief = authenticated_client.post(
        f"/api/v1/studio/briefs/from-idea/{idea['id']}",
        json={},
    ).json()
    response = authenticated_client.post(
        f"/api/v1/studio/briefs/{brief['id']}/scripts",
        json={
            "body_text": "Too short",
            "hook_selected": "No",
            "cta": "Go",
            "duration_seconds": 5,
        },
    )
    assert response.status_code == 422
