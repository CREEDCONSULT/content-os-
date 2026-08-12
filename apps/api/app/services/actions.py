from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime, time, timedelta
from datetime import date as date_type
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
    CalendarEvent,
    CanonicalStatus,
    ContentItem,
    ConversationSession,
    Experiment,
    Idea,
    MemoryRecord,
    PipelineStatus,
    ProposedDashboardAction,
    RiskLevel,
)
from app.schemas.contracts import (
    DashboardActionExecutionResult,
    IdeaCreate,
    ProposedDashboardActionCreate,
)

SAFE_ACTIONS = {"create_rough_idea", "create_campaign_plan"}

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


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:96] or "campaign"


def _parse_date(value: object, fallback: date_type) -> date_type:
    if isinstance(value, date_type):
        return value
    if isinstance(value, str):
        try:
            return date_type.fromisoformat(value[:10])
        except ValueError:
            return fallback
    return fallback


def _campaign_days(payload: dict[str, Any]) -> list[dict[str, Any]]:
    days = payload.get("days")
    if not isinstance(days, list):
        return []
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(days[:10], 1):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or f"Campaign day {index}").strip()[:240]
        normalized.append(
            {
                **item,
                "day": int(item.get("day") or index),
                "title": title or f"Campaign day {index}",
                "platform": str(item.get("platform") or "LinkedIn")[:60],
                "format": str(item.get("format") or "Post")[:80],
                "pillar": str(item.get("pillar") or "Build")[:80],
                "series": str(item.get("series") or "Building Creed")[:120],
                "audience": str(
                    item.get("audience") or payload.get("audience") or "Emerging Builder"
                )[:160],
                "objective": str(
                    item.get("objective")
                    or "Move the audience from inspiration into a specific builder action."
                )[:240],
                "status": str(item.get("status") or "brief"),
                "priority": str(item.get("priority") or "high")[:30],
            }
        )
    return normalized


def _markdown_list(items: list[Any]) -> str:
    if not items:
        return "- Not supplied."
    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            label = item.get("source") or item.get("type") or item.get("title") or "item"
            finding = item.get("finding") or item.get("summary") or item.get("impact") or item
            lines.append(f"- **{label}:** {finding}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _render_campaign_markdown(payload: dict[str, Any], days: list[dict[str, Any]]) -> str:
    strategy = (
        payload.get("rollout_strategy")
        if isinstance(payload.get("rollout_strategy"), dict)
        else {}
    )
    thesis = (
        str(payload.get("thesis"))
        if payload.get("thesis")
        else "Use visible systems, proof, and disciplined execution to build trust."
    )
    research_basis = (
        payload.get("research_basis")
        if isinstance(payload.get("research_basis"), list)
        else []
    )
    experiments = (
        payload.get("experiments")
        if isinstance(payload.get("experiments"), list)
        else []
    )
    sections = [
        f"# {payload.get('campaign_name', '10-Day BrandOS Campaign')}",
        "",
        "## Campaign thesis",
        thesis,
        "",
        "## Audience",
        str(payload.get("audience") or "Emerging builders and operators."),
        "",
        "## Research and analysis basis",
        _markdown_list(research_basis),
        "",
        "## Rollout strategy",
        _markdown_list(
            [
                {"source": key.replace("_", " ").title(), "finding": value}
                for key, value in strategy.items()
            ]
        ),
        "",
        "## 10-day rollout",
    ]
    for day in days:
        sections.extend(
            [
                "",
                f"### Day {day['day']}: {day['title']}",
                f"- Date: {day.get('date', 'TBD')}",
                f"- Platform / format: {day['platform']} / {day['format']}",
                f"- Pillar / series: {day['pillar']} / {day['series']}",
                f"- Objective: {day['objective']}",
                f"- Hook: {day.get('hook', 'TBD')}",
                f"- Core message: {day.get('core_message', 'TBD')}",
                f"- Proof angle: {day.get('proof_angle', 'TBD')}",
                f"- Research angle: {day.get('research_angle', 'TBD')}",
                f"- Production notes: {day.get('production_notes', 'TBD')}",
                f"- CTA: {day.get('cta', 'TBD')}",
                f"- Success metric: {day.get('success_metric', 'TBD')}",
            ]
        )
    sections.extend(
        [
            "",
            "## Experiments",
            _markdown_list(experiments),
            "",
            "## Approval boundaries",
            _markdown_list(
                payload.get("approval_boundaries")
                if isinstance(payload.get("approval_boundaries"), list)
                else []
            ),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def _safe_campaign_start(payload: dict[str, Any]) -> date_type:
    tomorrow = datetime.now(UTC).date() + timedelta(days=1)
    return _parse_date(payload.get("campaign_start"), tomorrow)


def _calendar_block_for_day(
    *,
    campaign_start: date_type,
    day: dict[str, Any],
) -> tuple[datetime, datetime, str]:
    day_date = _parse_date(
        day.get("date"),
        campaign_start + timedelta(days=max(0, int(day.get("day", 1)) - 1)),
    )
    start_at = datetime.combine(day_date, time(hour=14), tzinfo=UTC)
    end_at = start_at + timedelta(hours=1)
    notes = "\n".join(
        [
            f"Hook: {day.get('hook', 'TBD')}",
            f"Core message: {day.get('core_message', 'TBD')}",
            f"Production notes: {day.get('production_notes', 'TBD')}",
            "Internal BrandOS planning block only; public scheduling remains approval-gated.",
        ]
    )
    return start_at, end_at, notes


def _execute_create_campaign_plan(
    db: Session,
    action: ProposedDashboardAction,
    user: UserPrincipal,
) -> AgentToolCall:
    payload = dict(action.payload or {})
    days = _campaign_days(payload)
    if len(days) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="create_campaign_plan requires a payload.days array with 10 campaign days.",
        )
    campaign_name = str(payload.get("campaign_name") or "10-Day BrandOS Campaign")[:240]
    campaign_start = _safe_campaign_start(payload)
    markdown = _render_campaign_markdown(payload, days)
    checksum = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    vault_path = (
        f"02_Content_Strategy/Campaigns/"
        f"{campaign_start.isoformat()}-{_slug(campaign_name)}-{action.id[:8]}.md"
    )

    memory = MemoryRecord(
        brand_id=action.brand_id,
        memory_type="campaign_plan",
        title=campaign_name,
        content=markdown,
        canonical_status=CanonicalStatus.WORKING,
        confidence=float(payload.get("confidence") or 0.82),
        provenance={
            "source": "agent_action",
            "proposed_dashboard_action_id": action.id,
            "agent_run_id": action.agent_run_id,
        },
        vault_path=vault_path,
        content_checksum=checksum,
        sensitivity="internal",
        sync_status="database_only",
        embedding_status="disabled",
        is_demo=action.is_demo,
    )
    db.add(memory)
    db.flush()

    content_ids: list[str] = []
    calendar_ids: list[str] = []
    for day in days:
        due_date = _parse_date(
            day.get("date"),
            campaign_start + timedelta(days=max(0, int(day["day"]) - 1)),
        )
        content = ContentItem(
            brand_id=action.brand_id,
            idea_id=None,
            title=str(day["title"])[:240],
            platform=str(day["platform"])[:60],
            format=str(day["format"])[:80],
            pillar=str(day["pillar"])[:80],
            series=str(day["series"])[:120],
            audience=str(day["audience"])[:160],
            objective=str(day["objective"])[:240],
            status=PipelineStatus.BRIEF,
            priority=str(day["priority"])[:30],
            due_date=due_date,
            publish_at=None,
            readiness_score=42,
            approval_status=ApprovalStatus.NOT_REQUIRED,
            blocker=(
                "Needs final script, fact-check, and approval before production or publication."
            ),
            is_demo=action.is_demo,
        )
        db.add(content)
        db.flush()
        content_ids.append(content.id)
        start_at, end_at, notes = _calendar_block_for_day(
            campaign_start=campaign_start,
            day=day,
        )
        event = CalendarEvent(
            brand_id=action.brand_id,
            content_item_id=content.id,
            title=f"Prepare: {content.title[:220]}",
            event_type="write",
            start_at=start_at,
            end_at=end_at,
            timezone="America/Toronto",
            status="planned",
            capacity_units=1,
            notes=notes,
            is_demo=action.is_demo,
        )
        db.add(event)
        db.flush()
        calendar_ids.append(event.id)

    experiment_ids: list[str] = []
    experiments = payload.get("experiments")
    if isinstance(experiments, list):
        for item in experiments[:4]:
            if not isinstance(item, dict):
                continue
            experiment = Experiment(
                brand_id=action.brand_id,
                title=str(item.get("title") or f"{campaign_name} experiment")[:240],
                question=str(item.get("question") or "Which campaign variable improves saves?")[
                    :5000
                ],
                hypothesis=str(
                    item.get("hypothesis")
                    or "A clearer proof-led hook should improve qualified saves and replies."
                )[:5000],
                variable=str(item.get("variable") or "hook framing")[:240],
                control_conditions=list(
                    dict.fromkeys(
                        str(condition).strip()
                        for condition in item.get(
                            "control_conditions",
                            ["Same topic", "Same format", "Same posting window"],
                        )
                        if str(condition).strip()
                    )
                )[:20]
                or ["Same topic"],
                platform=str(item.get("platform") or "LinkedIn")[:60],
                content_type=str(item.get("content_type") or "Founder content")[:80],
                expected_outcome=str(
                    item.get("expected_outcome")
                    or "Higher save rate and more substantive replies."
                )[:5000],
                success_metric=str(item.get("success_metric") or "Save rate")[:240],
                measurement_start=_parse_date(item.get("measurement_start"), campaign_start),
                measurement_end=_parse_date(
                    item.get("measurement_end"),
                    campaign_start + timedelta(days=10),
                ),
                status="planned",
                confidence=0.0,
                is_demo=action.is_demo,
            )
            db.add(experiment)
            db.flush()
            experiment_ids.append(experiment.id)

    tool_call = AgentToolCall(
        brand_id=action.brand_id,
        session_id=action.session_id,
        agent_run_id=action.agent_run_id,
        tool_name=action.action_type,
        tool_type="safe_internal_orchestration",
        input_json=action.payload,
        output_json={
            "record_type": "campaign_plan",
            "record_id": memory.id,
            "campaign_name": campaign_name,
            "content_item_ids": content_ids,
            "calendar_event_ids": calendar_ids,
            "experiment_ids": experiment_ids,
            "vault_path": vault_path,
            "boundary": "Internal planning only; public posting remains approval-gated.",
        },
        status="completed",
        is_demo=action.is_demo,
    )
    db.add(tool_call)
    action.status = "executed"
    action.target_type = "campaign_plan"
    action.target_id = memory.id
    action.executed_at = datetime.now(UTC)
    action.result_json = tool_call.output_json
    db.add(
        AuditEvent(
            brand_id=action.brand_id,
            event_type="campaign_plan.created",
            actor=user.username,
            target_type="campaign_plan",
            target_id=memory.id,
            summary=f'10-day campaign staged by agent action: "{campaign_name}"',
            details={
                "proposed_dashboard_action_id": action.id,
                "agent_run_id": action.agent_run_id,
                "content_item_count": len(content_ids),
                "calendar_event_count": len(calendar_ids),
                "experiment_count": len(experiment_ids),
                "vault_path": vault_path,
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

    if action.action_type == "create_campaign_plan":
        tool_call = _execute_create_campaign_plan(db, action, user)
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
        elif record_type in {"campaign", "campaign_plan"} and normalized_action in {
            "create",
            "create_campaign",
            "create_campaign_plan",
            "stage_campaign",
            "stage_campaign_plan",
        }:
            action_type = "create_campaign_plan"
        else:
            return None

    payload: dict[str, Any] = {}
    raw_payload = write.get("payload")
    if isinstance(raw_payload, dict):
        payload = dict(raw_payload)
    elif isinstance(write.get("payload_json"), str):
        try:
            parsed_payload = json.loads(str(write["payload_json"]))
            if isinstance(parsed_payload, dict):
                payload = parsed_payload
        except json.JSONDecodeError:
            payload = {}
    if action_type == "create_rough_idea":
        raw_input = dict(run.input_envelope.get("raw_input") or {})
        content_text = str(raw_input.get("content_text") or raw_input.get("text") or "").strip()
        if not content_text and isinstance(payload.get("raw_input"), str):
            content_text = str(payload["raw_input"]).strip()
        if not content_text:
            return None
        payload = {
            "title": str(payload.get("title") or _title_from_original_input(raw_input))[:240],
            "raw_input": content_text,
            "source_type": payload.get("source_type") or raw_input.get("channel") or run.channel,
            "source_reference": payload.get("source_reference") or f"agent_run:{run.id}",
            "pillar": payload.get("pillar"),
            "series": payload.get("series"),
            "audience": payload.get("audience") or "Emerging Builder",
            "platform_fit": payload.get("platform_fit") or [],
            "strategic_objective": payload.get("strategic_objective"),
            "urgency": payload.get("urgency") or "normal",
        }
    elif action_type == "create_campaign_plan":
        if len(_campaign_days(payload)) < 10:
            return None

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
        existing = db.scalar(
            select(ProposedDashboardAction).where(
                ProposedDashboardAction.brand_id == run.brand_id,
                ProposedDashboardAction.agent_run_id == run.id,
                ProposedDashboardAction.action_type == proposal.action_type,
                ProposedDashboardAction.rationale == proposal.rationale,
            )
        )
        if existing:
            created.append(existing)
            continue
        created.append(create_dashboard_action(db, proposal, user, commit=False))
    return created
