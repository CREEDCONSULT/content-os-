from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


def _approved_script(client: TestClient) -> dict[str, object]:
    idea_response = client.post(
        "/api/v1/ideas",
        json={
            "title": "Production readiness test",
            "raw_input": (
                "Explain how a governed production checklist keeps a useful idea from "
                "becoming an unreliable publishing promise."
            ),
            "pillar": "Build",
            "audience": "Emerging Builder",
            "platform_fit": ["LinkedIn"],
        },
    )
    assert idea_response.status_code == 201
    idea = idea_response.json()
    brief_response = client.post(
        f"/api/v1/studio/briefs/from-idea/{idea['id']}",
        json={"platform": "LinkedIn", "format": "Video"},
    )
    assert brief_response.status_code == 201
    brief = brief_response.json()
    script_response = client.post(
        f"/api/v1/studio/briefs/{brief['id']}/scripts",
        json={
            "body_text": (
                "A production plan turns intention into evidence. Confirm the location, "
                "protect the approved script, prepare the tools, and make every blocker "
                "visible before the camera starts."
            ),
            "hook_selected": "A shoot is not ready because it is on the calendar.",
            "hook_variants": ["The hidden cost of an unplanned shoot is unreliable proof."],
            "cta": "What blocker will you make visible before your next shoot?",
            "duration_seconds": 60,
            "brand_alignment_score": 9.2,
            "originality_score": 8.8,
            "change_summary": "Create production test script",
        },
    )
    assert script_response.status_code == 201
    script = script_response.json()

    premature = client.post(f"/api/v1/production/plans/from-script/{script['id']}")
    assert premature.status_code == 409

    checked = client.post(
        f"/api/v1/studio/scripts/{script['id']}/fact-check",
        json={
            "claim_table": [],
            "sources": [],
            "unresolved_claims": [],
            "verified_text": script["current_version"]["body_text"],
            "confidence": 0.96,
        },
    )
    assert checked.status_code == 200
    submitted = client.post(f"/api/v1/studio/scripts/{script['id']}/submit")
    assert submitted.status_code == 200
    approved = client.post(
        f"/api/v1/approvals/{submitted.json()['approval_id']}/decision",
        json={"decision": "approved", "notes": "Approved for production test."},
    )
    assert approved.status_code == 200
    return client.get(f"/api/v1/studio/scripts/{script['id']}").json()


def test_calendar_enforces_hours_and_event_type_capacity(
    authenticated_client: TestClient,
) -> None:
    capacity = authenticated_client.put(
        "/api/v1/calendar/capacity",
        json={
            "week_start": "2026-09-09",
            "available_hours": 4,
            "max_shoots": 1,
            "max_edits": 1,
            "fallback_plan": "Publish one verified low-production build note instead.",
        },
    )
    assert capacity.status_code == 200
    assert capacity.json()["week_start"] == "2026-09-07"

    first = authenticated_client.post(
        "/api/v1/calendar/events",
        json={
            "title": "Founder shoot",
            "event_type": "shoot",
            "start_at": "2026-09-08T14:00:00Z",
            "end_at": "2026-09-08T16:00:00Z",
            "capacity_units": 2,
        },
    )
    assert first.status_code == 201

    shoot_conflict = authenticated_client.post(
        "/api/v1/calendar/events",
        json={
            "title": "Second founder shoot",
            "event_type": "shoot",
            "start_at": "2026-09-09T14:00:00Z",
            "end_at": "2026-09-09T15:00:00Z",
            "capacity_units": 1,
        },
    )
    assert shoot_conflict.status_code == 409
    assert "shoot capacity" in shoot_conflict.json()["detail"].lower()

    hours_conflict = authenticated_client.post(
        "/api/v1/calendar/events",
        json={
            "title": "Long research block",
            "event_type": "research",
            "start_at": "2026-09-10T13:00:00Z",
            "end_at": "2026-09-10T16:00:00Z",
            "capacity_units": 3,
        },
    )
    assert hours_conflict.status_code == 409
    assert "capacity exceeded" in hours_conflict.json()["detail"].lower()


def test_approved_script_requires_blocker_free_production_plan(
    authenticated_client: TestClient,
) -> None:
    script = _approved_script(authenticated_client)
    content_id = script["content_item_id"]

    bypass = authenticated_client.post(
        f"/api/v1/content/{content_id}/transition",
        json={"to_status": "ready_to_shoot"},
    )
    assert bypass.status_code == 403

    created = authenticated_client.post(f"/api/v1/production/plans/from-script/{script['id']}")
    assert created.status_code == 201
    plan = created.json()
    assert plan["status"] == "blocked"
    assert plan["readiness_score"] < 100
    assert len(plan["scenes"]) == 3
    assert len(plan["shots"]) == 6

    scheduled = authenticated_client.patch(
        f"/api/v1/production/plans/{plan['id']}",
        json={
            "location": "Quiet founder studio",
            "scheduled_at": "2026-08-11T14:00:00Z",
        },
    )
    assert scheduled.status_code == 200
    plan = scheduled.json()
    assert plan["status"] == "blocked"

    for item in plan["checklist"]:
        if item["phase"] == "pre_shoot" and item["is_critical"] and not item["is_complete"]:
            response = authenticated_client.post(
                f"/api/v1/production/checklist/{item['id']}",
                json={"is_complete": True},
            )
            assert response.status_code == 200
            plan = response.json()

    assert plan["status"] == "ready"
    assert plan["readiness_score"] == 100
    assert plan["blockers"] == []
    content = authenticated_client.get(f"/api/v1/content/{content_id}").json()
    assert content["status"] == "ready_to_shoot"


def test_asset_upload_preserves_original_and_detects_duplicate(
    authenticated_client: TestClient,
    tmp_path: Path,
) -> None:
    settings = Settings(
        app_env="test",
        object_storage_path=str(tmp_path),
        database_url="sqlite+pysqlite://",
    )
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        first = authenticated_client.post(
            "/api/v1/assets",
            data={
                "rights_status": "owned",
                "rights_notes": "Created in-house.",
                "tags": "founder, studio, founder",
            },
            files={"file": ("proof.txt", b"immutable source bytes", "text/plain")},
        )
        assert first.status_code == 201
        asset = first.json()
        assert asset["original_preserved"] is True
        assert asset["rights_status"] == "owned"
        assert asset["tags"] == ["founder", "studio"]
        assert (tmp_path / asset["storage_key"]).read_bytes() == b"immutable source bytes"

        duplicate = authenticated_client.post(
            "/api/v1/assets",
            data={"rights_status": "unknown"},
            files={"file": ("copy.txt", b"immutable source bytes", "text/plain")},
        )
        assert duplicate.status_code == 201
        assert duplicate.json()["duplicate_of_id"] == asset["id"]
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_proof_requires_evidence_and_client_permission(
    authenticated_client: TestClient,
) -> None:
    base = {
        "title": "BrandOS production proof",
        "proof_type": "build_log",
        "credibility_gap": "Can the workflow enforce readiness?",
        "context": "A governed local-first production workflow was required.",
        "constraints": "No public publishing and no fabricated evidence.",
        "process": "Built the workflow and exercised the readiness boundary.",
        "output": "A production plan with scenes, shots, and checklist records.",
        "result": "The plan stayed blocked until every pre-shoot gate passed.",
        "lessons": "Readiness must be computed from durable records.",
    }
    missing = authenticated_client.post("/api/v1/proof", json=base)
    assert missing.status_code == 201
    assert missing.json()["status"] == "evidence_needed"

    verified = authenticated_client.post(
        "/api/v1/proof",
        json={
            **base,
            "title": "Verified internal proof",
            "evidence_links": [{"label": "Local test report", "url": "local://validation"}],
        },
    )
    assert verified.status_code == 201
    assert verified.json()["status"] == "verified"

    confidential = authenticated_client.post(
        "/api/v1/proof",
        json={
            **base,
            "title": "Confidential client proof",
            "sensitivity": "client_confidential",
            "permission_status": "pending",
            "evidence_links": [{"label": "Private record", "url": "local://private"}],
        },
    )
    assert confidential.status_code == 201
    assert confidential.json()["status"] == "evidence_needed"
