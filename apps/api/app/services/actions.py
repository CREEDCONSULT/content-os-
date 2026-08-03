from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.db.models import (
    AgentRun,
    AgentToolCall,
    Approval,
    ApprovalStatus,
    AuditEvent,
    Brand,
    ConversationSession,
    Idea,
    ProposedDashboardAction,
    RiskLevel,
)
from app.schemas.contracts import (
    DashboardActionExecutionResult,
    IdeaCreate,
    ProposedDashboardActionCreate,
)

SAFE_ACTIONS = {"create_rough_idea"}

APPROVAL_REQUIRED_ACTIONS = {
    "analyze_external_document",
    "create_campaign_commitment",
    "promote_memory_to_canonical",
    "publish_content",
    "run_paid_research",
    "schedule_calendar_event",
    "schedule_post",
    "send_external_message",
    "update_content_calendar",
    "use_sensitive_founder_story",
}

SUPPORTED_ACTIONS = SAFE_ACTIONS | APPROVAL_REQUIRED_ACTIONS


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def _validate_optional_links(
    db: Session,
    brand: Brand,
    *,
    session_id: str | None,
    agent_run_id: str | None,
) -> None:
    if session_id:
        session = db.get(ConversationSession, session_id)
        if not session or session.brand_id != brand.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found.",
            )
    if agent_run_id:
        run = db.get(AgentRun, agent_run_id)
        if not run or run.brand_id != brand.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent run not found.",
            )


def _validated_action_type(action_type: str) -> str:
    normalized = action_type.strip()
    if normalized not in SUPPORTED_ACTIONS:
        supported = ", ".join(sorted(SUPPORTED_ACTIONS))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported action_type. Supported actions: {supported}.",
        )
    return normalized


def _safe_risk(action_type: str, risk_level: RiskLevel) -> RiskLevel:
    if action_type in SAFE_ACTIONS:
        return risk_level
    if risk_level == RiskLevel.LOW:
        return RiskLevel.HIGH
    return risk_level


def create_dashboard_action(
    db: Session,
    payload: ProposedDashboardActionCreate,
    user: UserPrincipal,
    *,
    commit: bool = True,
) -> ProposedDashboardAction:
    brand = _active_brand(db)
    action_type = _validated_action_type(payload.action_type)
    _validate_optional_links(
        db,
        brand,
        session_id=payload.session_id,
        agent_run_id=payload.agent_run_id,
    )
    action = ProposedDashboardAction(
        brand_id=brand.id,
        session_id=payload.session_id,
        agent_run_id=payload.agent_run_id,
        action_type=action_type,
        target_type=payload.target_type,
        target_id=payload.target_id,
        payload=payload.payload,
        rationale=payload.rationale,
        risk_level=_safe_risk(action_type, payload.risk_level),
        status="proposed",
        is_demo=payload.is_demo,
    )
    db.add(action)
    db.flush()
    db.add(
        AuditEvent(
            brand_id=brand.id,
            event_type="dashboard_action.proposed",
            actor=user.username,
            target_type="proposed_dashboard_action",
            target_id=action.id,
            summary=f"Dashboard action proposed: {action.action_type}",
            details={
                "session_id": action.session_id,
                "agent_run_id": action.agent_run_id,
                "risk_level": action.risk_level.value,
                "rationale": action.rationale,
            },
            is_demo=action.is_demo,
        )
    )
    if commit:
        db.commit()
        db.refresh(action)
    return action


def list_dashboard_actions(
    db: Session,
    *,
    status_filter: str | None,
    limit: int,
    offset: int = 0,
) -> tuple[list[ProposedDashboardAction], int]:
    brand = _active_brand(db)
    statement = select(ProposedDashboardAction).where(
        ProposedDashboardAction.brand_id == brand.id
    )
    count_statement = select(func.count(ProposedDashboardAction.id)).where(
        ProposedDashboardAction.brand_id == brand.id
    )
    if status_filter:
        statement = statement.where(ProposedDashboardAction.status == status_filter)
        count_statement = count_statement.where(ProposedDashboardAction.status == status_filter)
    items = list(
        db.scalars(
            statement.order_by(ProposedDashboardAction.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    total = db.scalar(count_statement) or 0
    return items, total


def list_agent_tool_calls(db: Session, *, limit: int, offset: int = 0) -> list[AgentToolCall]:
    brand = _active_brand(db)
    return list(
        db.scalars(
            select(AgentToolCall)
            .where(AgentToolCall.brand_id == brand.id)
            .order_by(AgentToolCall.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )


def _approval_for_action(
    db: Session,
    action: ProposedDashboardAction,
    user: UserPrincipal,
) -> Approval:
    if action.approval_id:
        approval = db.get(Approval, action.approval_id)
        if approval:
            return approval
    approval = Approval(
        brand_id=action.brand_id,
        action_type=action.action_type,
        target_type="proposed_dashboard_action",
        target_id=action.id,
        requested_by=user.username,
        risk_level=action.risk_level,
        cost_estimate=0,
        status=ApprovalStatus.PENDING,
        context={
            "session_id": action.session_id,
            "agent_run_id": action.agent_run_id,
            "target_type": action.target_type,
            "target_id": action.target_id,
            "payload": action.payload,
            "rationale": action.rationale,
        },
    )
    db.add(approval)
    db.flush()
    return approval


def _latest_tool_call_for_action(
    db: Session,
    action: ProposedDashboardAction,
) -> AgentToolCall | None:
    return db.scalar(
        select(AgentToolCall)
        .where(
            AgentToolCall.brand_id == action.brand_id,
            AgentToolCall.session_id == action.session_id,
            AgentToolCall.agent_run_id == action.agent_run_id,
            AgentToolCall.tool_name == action.action_type,
            AgentToolCall.approval_id == action.approval_id,
        )
        .order_by(AgentToolCall.created_at.desc())
        .limit(1)
    )


def _blocked_tool_call(
    db: Session,
    action: ProposedDashboardAction,
    approval: Approval,
) -> AgentToolCall:
    tool_call = AgentToolCall(
        brand_id=action.brand_id,
        session_id=action.session_id,
        agent_run_id=action.agent_run_id,
        tool_name=action.action_type,
        tool_type="approval_gate",
        input_json=action.payload,
        output_json={
            "approval_id": approval.id,
            "status": approval.status.value,
            "reason": "Human approval is required before this action can execute.",
        },
        status="blocked",
        approval_id=approval.id,
        is_demo=action.is_demo,
    )
    db.add(tool_call)
    db.flush()
    return tool_call


def _idea_payload_for_action(action: ProposedDashboardAction) -> IdeaCreate:
    try:
        return IdeaCreate(
            **{
                "source_type": "agent_action",
                "source_reference": f"proposed_dashboard_action:{action.id}",
                **action.payload,
            }
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid create_rough_idea payload: {exc.errors()}",
        ) from exc


def _execute_create_rough_idea(
    db: Session,
    action: ProposedDashboardAction,
    user: UserPrincipal,
) -> AgentToolCall:
    idea_payload = _idea_payload_for_action(action)
    idea = Idea(brand_id=action.brand_id, **idea_payload.model_dump(), is_demo=action.is_demo)
    db.add(idea)
    db.flush()
    tool_call = AgentToolCall(
        brand_id=action.brand_id,
        session_id=action.session_id,
        agent_run_id=action.agent_run_id,
        tool_name=action.action_type,
        tool_type="safe_write",
        input_json=action.payload,
        output_json={
            "record_type": "idea",
            "record_id": idea.id,
            "title": idea.title,
        },
        status="completed",
        is_demo=action.is_demo,
    )
    db.add(tool_call)
    action.status = "executed"
    action.target_type = "idea"
    action.target_id = idea.id
    action.executed_at = datetime.now(UTC)
    action.result_json = tool_call.output_json
    db.add(
        AuditEvent(
            brand_id=action.brand_id,
            event_type="idea.created",
            actor=user.username,
            target_type="idea",
            target_id=idea.id,
            summary=f'Idea captured by agent action: "{idea.title}"',
            details={
                "proposed_dashboard_action_id": action.id,
                "session_id": action.session_id,
                "agent_run_id": action.agent_run_id,
            },
            is_demo=action.is_demo,
        )
    )
    db.flush()
    return tool_call


def execute_dashboard_action(
    db: Session,
    action_id: str,
    user: UserPrincipal,
) -> DashboardActionExecutionResult:
    brand = _active_brand(db)
    action = db.get(ProposedDashboardAction, action_id)
    if not action or action.brand_id != brand.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposed dashboard action not found.",
        )

    if action.status == "approval_required" and action.approval_id:
        existing_call = _latest_tool_call_for_action(db, action)
        if existing_call:
            return DashboardActionExecutionResult(action=action, tool_call=existing_call)

    if action.status != "proposed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Action is already {action.status}.",
        )

    if action.action_type not in SAFE_ACTIONS or action.risk_level != RiskLevel.LOW:
        approval = _approval_for_action(db, action, user)
        tool_call = _blocked_tool_call(db, action, approval)
        action.status = "approval_required"
        action.approval_id = approval.id
        action.result_json = {
            "approval_id": approval.id,
            "status": approval.status.value,
        }
        db.commit()
        db.refresh(action)
        db.refresh(tool_call)
        return DashboardActionExecutionResult(action=action, tool_call=tool_call)

    if action.action_type == "create_rough_idea":
        tool_call = _execute_create_rough_idea(db, action, user)
        db.commit()
        db.refresh(action)
        db.refresh(tool_call)
        return DashboardActionExecutionResult(action=action, tool_call=tool_call)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"No executor is registered for {action.action_type}.",
    )


def _title_from_original_input(raw_input: dict[str, Any]) -> str:
    text = str(raw_input.get("content_text") or raw_input.get("text") or "").strip()
    if text.startswith("/idea"):
        text = text.removeprefix("/idea").strip()
    first_line = text.splitlines()[0].strip() if text else ""
    return first_line[:120] or "Agent proposed idea"


def _proposal_from_agent_write(
    write: dict[str, Any],
    *,
    run: AgentRun,
    session_id: str | None,
) -> ProposedDashboardActionCreate | None:
    action_type = str(write.get("action") or "").strip()
    record_type = str(write.get("record_type") or "").strip().lower()
    if action_type not in SUPPORTED_ACTIONS:
        normalized_action = action_type.lower().replace(" ", "_")
        if record_type == "idea" and normalized_action in {
            "create",
            "create_idea",
            "create_rough_idea",
            "save_idea",
            "capture_idea",
        }:
            action_type = "create_rough_idea"
        else:
            return None

    payload: dict[str, Any] = {}
    if action_type == "create_rough_idea":
        raw_input = dict(run.input_envelope.get("raw_input") or {})
        content_text = str(raw_input.get("content_text") or raw_input.get("text") or "").strip()
        if not content_text:
            return None
        payload = {
            "title": _title_from_original_input(raw_input),
            "raw_input": content_text,
            "source_type": raw_input.get("channel") or run.channel,
            "source_reference": f"agent_run:{run.id}",
            "audience": "Emerging Builder",
            "platform_fit": [],
        }

    risk_level = RiskLevel.LOW if action_type in SAFE_ACTIONS else RiskLevel.HIGH
    return ProposedDashboardActionCreate(
        session_id=session_id,
        agent_run_id=run.id,
        action_type=action_type,
        target_type=record_type or None,
        payload=payload,
        rationale=str(write.get("rationale") or f"Agent proposed {action_type}."),
        risk_level=risk_level,
        is_demo=run.is_demo,
    )


def create_actions_from_agent_run(
    db: Session,
    run: AgentRun,
    user: UserPrincipal,
    *,
    session_id: str | None,
) -> list[ProposedDashboardAction]:
    created: list[ProposedDashboardAction] = []
    for write in run.proposed_writes or []:
        if not isinstance(write, dict):
            continue
        proposal = _proposal_from_agent_write(write, run=run, session_id=session_id)
        if not proposal:
            continue
        created.append(create_dashboard_action(db, proposal, user, commit=False))
    return created
