from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import TelegramMessage
from app.db.session import get_db
from app.schemas.contracts import TelegramCapture, TelegramMessageView
from app.services.telegram import capture_fixture, capture_webhook_update

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/webhook", response_model=TelegramMessageView)
def webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TelegramMessage:
    return capture_webhook_update(
        db,
        settings,
        update,
        x_telegram_bot_api_secret_token,
    )


@router.post(
    "/capture-test",
    response_model=TelegramMessageView,
    dependencies=[Depends(require_user)],
)
def capture_test(
    payload: TelegramCapture,
    db: Session = Depends(get_db),
) -> TelegramMessage:
    return capture_fixture(db, payload)


@router.get(
    "/messages",
    response_model=list[TelegramMessageView],
    dependencies=[Depends(require_user)],
)
def list_messages(db: Session = Depends(get_db)) -> list[TelegramMessage]:
    return list(
        db.scalars(
            select(TelegramMessage).order_by(TelegramMessage.created_at.desc()).limit(100)
        ).all()
    )
