from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.core.config import Settings, get_settings
from app.db.models import ConversationMessage
from app.db.session import get_db
from app.schemas.contracts import (
    ConversationList,
    ConversationMessageView,
    ConversationSessionView,
    ConversationTurnCreate,
    ConversationTurnResult,
)
from app.services.conversations import (
    get_conversation_session,
    list_conversation_messages,
    list_conversation_sessions,
    process_dashboard_turn,
)

router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["conversations"],
    dependencies=[Depends(require_user)],
)


@router.get("", response_model=ConversationList)
def list_sessions(
    channel: str | None = Query(default=None, pattern="^(dashboard|telegram|voice|api)$"),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ConversationList:
    items, total = list_conversation_sessions(db, channel=channel, limit=limit)
    return ConversationList(items=items, total=total)


@router.post(
    "/messages",
    response_model=ConversationTurnResult,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    payload: ConversationTurnCreate,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
    settings: Settings = Depends(get_settings),
) -> ConversationTurnResult:
    return process_dashboard_turn(db, settings, payload, user)


@router.get("/{session_id}", response_model=ConversationSessionView)
def get_session(session_id: str, db: Session = Depends(get_db)):
    return get_conversation_session(db, session_id)


@router.get("/{session_id}/messages", response_model=list[ConversationMessageView])
def list_messages(
    session_id: str,
    limit: int = Query(default=100, ge=1, le=300),
    db: Session = Depends(get_db),
) -> list[ConversationMessage]:
    return list_conversation_messages(db, session_id, limit=limit)
