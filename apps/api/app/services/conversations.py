from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.core.config import Settings
from app.db.models import Brand, ConversationMessage, ConversationSession
from app.schemas.contracts import AgentRunCreate, ConversationTurnCreate, ConversationTurnResult
from app.services.actions import create_actions_from_agent_run
from app.services.agent import execute_agent_run

MAX_TELEGRAM_REPLY_CHARS = 3800


@dataclass
class ConversationTurn:
    session: ConversationSession
    user_message: ConversationMessage
    agent_message: ConversationMessage | None
    agent_run: Any | None
    reply_text: str
    outbound: dict[str, Any]


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def _title_from_text(text: str, channel: str) -> str:
    normalized = " ".join(text.strip().split())
    if normalized:
        return normalized[:120]
    return f"{channel.title()} conversation"


def _intent_from_text(text: str, channel: str) -> str:
    normalized = text.strip()
    lowered = normalized.lower()
    if lowered.startswith("/idea"):
        return "Capture and develop a rough BrandOS idea"
    if lowered.startswith("/benchmark") or lowered.startswith("/watch") or "http" in lowered:
        return "Review a creator benchmark or reference"
    if lowered.startswith("/research"):
        return "Research and synthesize a BrandOS topic"
    if lowered.startswith("/script"):
        return "Develop a content script through BrandOS"
    if lowered.startswith("/calendar"):
        return "Plan or inspect the BrandOS content calendar"
    prefix = "Telegram conversation" if channel == "telegram" else "Dashboard conversation"
    return f"{prefix}: {normalized[:180]}"[:240] if normalized else prefix


def _conversation_user(channel: str, sender_id: str, fallback: UserPrincipal) -> UserPrincipal:
    if channel != "telegram":
        return fallback
    return UserPrincipal(
        username=f"telegram:{sender_id}",
        display_name="Telegram founder",
        permissions=("read", "draft", "internal_write"),
    )


def _recent_messages(db: Session, session_id: str, limit: int = 8) -> list[dict[str, Any]]:
    messages = list(
        db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        ).all()
    )
    messages.reverse()
    return [
        {
            "sender_type": message.sender_type,
            "message_type": message.message_type,
            "content_text": message.content_text[:1200],
            "status": message.status,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]


def _find_or_create_session(
    db: Session,
    brand: Brand,
    *,
    channel: str,
    external_thread_id: str,
    title_seed: str,
    is_demo: bool,
    session_id: str | None = None,
) -> ConversationSession:
    if session_id:
        session = db.get(ConversationSession, session_id)
        if not session or session.brand_id != brand.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found.",
            )
        return session
    session = db.scalar(
        select(ConversationSession).where(
            ConversationSession.brand_id == brand.id,
            ConversationSession.channel == channel,
            ConversationSession.external_thread_id == external_thread_id,
        )
    )
    if session:
        return session
    now = datetime.now(UTC)
    session = ConversationSession(
        brand_id=brand.id,
        channel=channel,
        external_thread_id=external_thread_id,
        title=_title_from_text(title_seed, channel),
        status="active",
        current_intent=None,
        active_agent="brand_director",
        memory_scope="rough",
        last_message_at=now,
        summary="",
        open_questions=[],
        proposed_action_count=0,
        approval_count=0,
        is_demo=is_demo,
    )
    db.add(session)
    db.flush()
    return session


def _format_reply(run: Any | None, content_text: str, channel: str) -> str:
    if not run:
        return "I saved this in the conversation, but no agent run was needed yet."
    if run.status == "blocked":
        action = run.approvals_required[0]["action_type"] if run.approvals_required else "approval"
        return (
            "I can help with this, but BrandOS correctly paused before taking a risky action. "
            f"It needs approval for {action.replace('_', ' ')}. "
            "Open the dashboard approval queue when you want to decide."
        )[:MAX_TELEGRAM_REPLY_CHARS]
    if run.status == "failed":
        return (
            "I preserved your message, but the agent runtime could not complete safely. "
            f"{run.summary} Check the Agent Console for the exact configuration note."
        )[:MAX_TELEGRAM_REPLY_CHARS]

    summary = (run.summary or "").strip()
    next_action = run.next_actions[0] if run.next_actions else None
    if channel == "telegram":
        lead = (
            "I'm with you — I routed this through the BrandOS agent and kept it in "
            "rough-work mode."
        )
        if content_text.strip().startswith("/idea"):
            lead = "Got it — I saved the rough idea and also thought through the next move."
        elif "http" in content_text:
            lead = (
                "Got it — I treated that as a reference/benchmark and kept the "
                "analysis cautious."
            )
        reply = f"{lead}\n\n{summary}"
        if next_action:
            reply = f"{reply}\n\nNext: {next_action}"
        return reply[:MAX_TELEGRAM_REPLY_CHARS]
    return summary[:MAX_TELEGRAM_REPLY_CHARS]


def process_conversation_turn(
    db: Session,
    settings: Settings,
    *,
    user: UserPrincipal,
    channel: str,
    sender_id: str,
    content_text: str,
    message_type: str = "text",
    content_json: dict[str, Any] | None = None,
    external_thread_id: str | None = None,
    session_id: str | None = None,
    source_reference: str | None = None,
    telegram_update_id: str | None = None,
    telegram_message_id: str | None = None,
    is_demo: bool = False,
    outbound: dict[str, Any] | None = None,
) -> ConversationTurnResult:
    brand = _active_brand(db)
    thread_id = external_thread_id or f"{channel}:{sender_id}"
    session = _find_or_create_session(
        db,
        brand,
        channel=channel,
        external_thread_id=thread_id,
        title_seed=content_text,
        is_demo=is_demo,
        session_id=session_id,
    )
    user_message = ConversationMessage(
        brand_id=brand.id,
        session_id=session.id,
        channel=channel,
        sender_type="user",
        sender_id=sender_id,
        message_type=message_type,
        content_text=content_text,
        content_json=content_json or {},
        source_reference=source_reference,
        telegram_update_id=telegram_update_id,
        telegram_message_id=telegram_message_id,
        attachment_ids=[],
        sensitivity="internal",
        status="processing",
        is_demo=is_demo,
    )
    db.add(user_message)
    db.flush()

    recent_messages = _recent_messages(db, session.id)
    intent = _intent_from_text(content_text, channel)
    agent_user = _conversation_user(channel, sender_id, user)
    run = execute_agent_run(
        db,
        AgentRunCreate(
            request_id=str(uuid.uuid4()),
            idempotency_key=(
                f"{channel}:{telegram_update_id}:agent"
                if telegram_update_id
                else f"{channel}:{session.id}:{user_message.id}:agent"
            ),
            channel="telegram" if channel == "telegram" else "dashboard",
            intent=intent,
            raw_input={
                "conversation_session_id": session.id,
                "conversation_message_id": user_message.id,
                "channel": channel,
                "message_type": message_type,
                "content_text": content_text,
                "content_json": content_json or {},
                "source_reference": source_reference,
                "recent_messages": recent_messages,
                "mode": "rough_work_conversation",
            },
        ),
        agent_user,
        settings,
    )
    user_message.agent_run_id = run.id
    user_message.status = "responded" if run.status != "failed" else "failed"
    proposed_actions = create_actions_from_agent_run(
        db,
        run,
        agent_user,
        session_id=session.id,
    )
    reply_text = _format_reply(run, content_text, channel)

    agent_message = ConversationMessage(
        brand_id=brand.id,
        session_id=session.id,
        channel=channel,
        sender_type="agent",
        sender_id="brand_director",
        message_type="text",
        content_text=reply_text,
        content_json={
            "agent_run_id": run.id,
            "agent_status": run.status,
            "skills_used": run.skills_used,
            "approvals_required": run.approvals_required,
            "proposed_writes": run.proposed_writes,
            "proposed_dashboard_actions": [
                {
                    "id": action.id,
                    "action_type": action.action_type,
                    "risk_level": action.risk_level.value,
                    "status": action.status,
                }
                for action in proposed_actions
            ],
        },
        source_reference=f"agent_run:{run.id}",
        telegram_update_id=telegram_update_id,
        telegram_message_id=None,
        attachment_ids=[],
        agent_run_id=run.id,
        sensitivity="internal",
        status="sent" if run.status != "failed" else "failed",
        is_demo=is_demo or run.is_demo,
    )
    db.add(agent_message)

    session.last_message_at = datetime.now(UTC)
    session.current_intent = intent
    session.summary = run.summary[:4000]
    session.proposed_action_count += len(proposed_actions)
    session.approval_count += len(run.approvals_required or [])
    session.status = "active" if run.status != "failed" else "paused"
    db.commit()
    db.refresh(session)
    db.refresh(user_message)
    db.refresh(agent_message)
    db.refresh(run)

    return ConversationTurnResult(
        session=session,
        user_message=user_message,
        agent_message=agent_message,
        agent_run=run,
        reply_text=reply_text,
        outbound=outbound or {},
    )


def process_dashboard_turn(
    db: Session,
    settings: Settings,
    payload: ConversationTurnCreate,
    user: UserPrincipal,
) -> ConversationTurnResult:
    return process_conversation_turn(
        db,
        settings,
        user=user,
        channel=payload.channel,
        sender_id=user.username,
        content_text=payload.content_text,
        message_type=payload.message_type,
        content_json=payload.content_json,
        external_thread_id=payload.external_thread_id or f"dashboard:{user.username}",
        session_id=payload.session_id,
        source_reference=payload.source_reference,
        is_demo=False,
    )


def list_conversation_sessions(
    db: Session,
    *,
    channel: str | None,
    limit: int,
) -> tuple[list[ConversationSession], int]:
    brand = _active_brand(db)
    statement = select(ConversationSession).where(ConversationSession.brand_id == brand.id)
    if channel:
        statement = statement.where(ConversationSession.channel == channel)
    items = list(
        db.scalars(statement.order_by(ConversationSession.last_message_at.desc()).limit(limit)).all()
    )
    count_statement = select(func.count(ConversationSession.id)).where(
        ConversationSession.brand_id == brand.id
    )
    if channel:
        count_statement = count_statement.where(ConversationSession.channel == channel)
    total = db.scalar(count_statement) or 0
    return items, total


def get_conversation_session(db: Session, session_id: str) -> ConversationSession:
    brand = _active_brand(db)
    session = db.get(ConversationSession, session_id)
    if not session or session.brand_id != brand.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found.",
        )
    return session


def list_conversation_messages(
    db: Session,
    session_id: str,
    *,
    limit: int,
) -> list[ConversationMessage]:
    session = get_conversation_session(db, session_id)
    return list(
        db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session.id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        ).all()
    )
