from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.core.config import Settings
from app.db.models import (
    AgentRun,
    Approval,
    ApprovalStatus,
    AuditEvent,
    Brand,
    RiskLevel,
)
from app.schemas.contracts import AgentRunCreate
from app.services.context import build_context_pack
from app.services.providers import ProviderConfigurationError, provider_for
from app.services.skills import load_skills, route_skill_slugs

HIGH_RISK_INTENTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("publish", "go live"), "public_publishing"),
    (("public schedule", "schedule publicly"), "public_scheduling"),
    (("outreach", "send message", "email creator"), "external_outreach"),
    (("delete", "destroy", "purge"), "destructive_deletion"),
    (("canonical", "brand boundary"), "canonical_brand_change"),
    (("redefine audience", "audience redefinition"), "audience_redefinition"),
    (("sensitive founder", "private founder story"), "sensitive_story_use"),
    (("investment signal", "buy recommendation", "sell recommendation"), "financial_content"),
)


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise RuntimeError("Active brand is unavailable.")
    return brand


def _approval_action(intent: str) -> str | None:
    normalized = intent.lower()
    for keywords, action in HIGH_RISK_INTENTS:
        if any(keyword in normalized for keyword in keywords):
            return action
    return None


def _spent_today(db: Session, brand_id: str) -> float:
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    return float(
        db.scalar(
            select(func.coalesce(func.sum(AgentRun.model_cost), 0)).where(
                AgentRun.brand_id == brand_id,
                AgentRun.created_at >= start,
            )
        )
        or 0
    )


def _create_approval(
    db: Session,
    run: AgentRun,
    action_type: str,
    user: UserPrincipal,
    context: dict[str, Any],
    cost_estimate: float = 0,
) -> Approval:
    approval = Approval(
        brand_id=run.brand_id,
        action_type=action_type,
        target_type="agent_run",
        target_id=run.id,
        requested_by=user.username,
        risk_level=RiskLevel.HIGH,
        cost_estimate=cost_estimate,
        status=ApprovalStatus.PENDING,
        context=context,
    )
    db.add(approval)
    db.flush()
    return approval


def execute_agent_run(
    db: Session,
    payload: AgentRunCreate,
    user: UserPrincipal,
    settings: Settings,
) -> AgentRun:
    if payload.idempotency_key:
        existing = db.scalar(
            select(AgentRun).where(AgentRun.idempotency_key == payload.idempotency_key)
        )
        if existing:
            return existing

    brand = _active_brand(db)
    request_id = payload.request_id or str(uuid.uuid4())
    input_envelope = {
        "request_id": request_id,
        "user_id": user.username,
        "brand_id": brand.id,
        "channel": payload.channel,
        "intent": payload.intent,
        "raw_input": payload.raw_input,
        "context_pack_id": None,
        "permissions": list(user.permissions),
        "budget": payload.budget.model_dump(),
        "approval_state": "none",
    }
    run = AgentRun(
        brand_id=brand.id,
        request_id=request_id,
        idempotency_key=payload.idempotency_key,
        channel=payload.channel,
        intent=payload.intent,
        status="running",
        provider=settings.ai_provider.lower(),
        model_alias=(
            "mock_brand_fast_model"
            if settings.ai_provider.lower() == "mock"
            else settings.brand_fast_model or "unconfigured"
        ),
        input_envelope=input_envelope,
        summary="Run created; routing and context assembly are in progress.",
    )
    db.add(run)
    db.flush()

    skill_slugs = route_skill_slugs(payload.intent, payload.raw_input)
    skills = load_skills(db, skill_slugs)
    resolved_slugs = [skill.slug for skill in skills]
    missing_slugs = [slug for slug in skill_slugs if slug not in resolved_slugs]
    pack = build_context_pack(db, brand.id, payload.intent, payload.raw_input)
    run.context_pack_id = pack.id
    run.skills_used = resolved_slugs or skill_slugs
    run.context_loaded = pack.source_records
    input_envelope["context_pack_id"] = pack.id
    run.input_envelope = input_envelope

    action_type = _approval_action(payload.intent)
    projected_spend = _spent_today(db, brand.id) + payload.budget.model_usd
    if projected_spend > settings.daily_model_budget_usd:
        action_type = "paid_tool_use_above_budget"

    if action_type:
        approval = _create_approval(
            db,
            run,
            action_type,
            user,
            {
                "intent": payload.intent,
                "context_pack_id": pack.id,
                "selected_skills": run.skills_used,
                "projected_daily_model_spend": projected_spend,
                "daily_model_budget": settings.daily_model_budget_usd,
            },
            cost_estimate=payload.budget.model_usd + payload.budget.tool_usd,
        )
        run.status = "blocked"
        run.approvals_required = [
            {
                "approval_id": approval.id,
                "action_type": action_type,
                "risk_level": approval.risk_level.value,
            }
        ]
        run.summary = f"Run blocked pending approval for {action_type.replace('_', ' ')}."
        run.next_actions = ["Review the pending approval in the Approval Queue."]
        run.output_envelope = {
            "skill": "00_skill_router",
            "status": "blocked",
            "summary": run.summary,
            "outputs": {
                "selected_skills": run.skills_used,
                "execution_plan": ["Wait for explicit human approval."],
                "context_pack_ids": [pack.id],
                "approval_requirements": run.approvals_required,
                "result_references": [],
            },
            "sources": pack.source_records,
            "memory_writes": [],
            "dashboard_writes": [],
            "approvals_required": run.approvals_required,
            "warnings": missing_slugs,
            "next_actions": run.next_actions,
            "confidence": 1.0,
        }
        run.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(run)
        return run

    try:
        result = provider_for(settings).generate(
            intent=payload.intent,
            raw_input=payload.raw_input,
            context_markdown=pack.context_markdown,
            selected_skills=run.skills_used,
        )
    except ProviderConfigurationError as exc:
        run.status = "failed"
        run.error = str(exc)
        run.summary = "Agent provider is not safely configured."
        run.next_actions = ["Configure the exact missing server-side provider values."]
        run.output_envelope = {
            "skill": "00_skill_router",
            "status": "failed",
            "summary": run.summary,
            "outputs": {},
            "sources": pack.source_records,
            "memory_writes": [],
            "dashboard_writes": [],
            "approvals_required": [],
            "warnings": [str(exc)],
            "next_actions": run.next_actions,
            "confidence": 0.0,
        }
        run.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(run)
        return run

    output = result.output
    run.provider = result.provider
    run.model_alias = result.model_alias
    run.status = "completed"
    run.summary = str(output["summary"])
    run.proposed_writes = list(output.get("proposed_writes", []))
    run.completed_writes = []
    run.next_actions = list(output.get("next_actions", []))
    run.confidence = float(output.get("confidence", 0))
    run.output_envelope = {
        "skill": "00_skill_router",
        "status": "success",
        "summary": run.summary,
        "outputs": {
            "selected_skills": run.skills_used,
            "execution_plan": [
                "Route the request.",
                "Load the smallest sufficient canonical context pack.",
                "Generate a structured draft without performing high-risk writes.",
            ],
            "context_pack_ids": [pack.id],
            "approval_requirements": [],
            "result_references": [],
            "provider_output": output,
            "provider_usage": result.usage,
        },
        "sources": pack.source_records,
        "memory_writes": [],
        "dashboard_writes": [],
        "approvals_required": [],
        "warnings": [*missing_slugs, *output.get("warnings", [])],
        "next_actions": run.next_actions,
        "confidence": run.confidence,
    }
    run.completed_at = datetime.now(UTC)
    db.add(
        AuditEvent(
            brand_id=brand.id,
            event_type="agent.run.completed",
            actor=user.username,
            target_type="agent_run",
            target_id=run.id,
            summary=run.summary[:500],
            details={
                "request_id": run.request_id,
                "skills": run.skills_used,
                "provider": run.provider,
                "context_pack_id": pack.id,
            },
            is_demo=result.provider == "mock",
        )
    )
    db.commit()
    db.refresh(run)
    return run
