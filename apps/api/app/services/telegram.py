from __future__ import annotations

import secrets
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import (
    BenchmarkContent,
    Brand,
    ContentItem,
    Idea,
    TelegramMessage,
)
from app.schemas.contracts import TelegramCapture


def _brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def verify_webhook(
    settings: Settings,
    sender_id: int,
    supplied_secret: str | None,
) -> None:
    if not settings.telegram_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram adapter is disabled.",
        )
    expected = (
        settings.telegram_webhook_secret.get_secret_value()
        if settings.telegram_webhook_secret
        else ""
    )
    if not expected or not supplied_secret or not secrets.compare_digest(expected, supplied_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram webhook secret is invalid.",
        )
    if sender_id not in settings.telegram_allowed_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Telegram sender is not allowlisted.",
        )


def _classify(content: str, message_type: str) -> str:
    normalized = content.strip().lower()
    if message_type == "voice":
        return "idea"
    if normalized.startswith("/status"):
        return "status"
    if normalized.startswith("/benchmark") or normalized.startswith("http"):
        return "benchmark"
    if normalized.startswith("/approve"):
        return "approval_request"
    return "idea"


def _capture(
    db: Session,
    *,
    update_id: str,
    sender_id: int,
    message_id: str | None,
    message_type: str,
    text: str | None,
    transcript: str | None,
    source_reference: str | None,
    is_simulation: bool,
) -> TelegramMessage:
    existing = db.scalar(select(TelegramMessage).where(TelegramMessage.update_id == update_id))
    if existing:
        return existing
    brand = _brand(db)
    content = (transcript or text or "").strip()
    classification = _classify(content, message_type)
    record_type: str | None = None
    record_id: str | None = None
    failure: str | None = None

    if message_type == "voice" and not transcript:
        message_status = "pending_transcription"
        response = (
            "Voice note preserved. Transcription is pending because no configured "
            "transcription provider is available."
        )
        failure = "BRAND_TRANSCRIPTION_MODEL is not configured."
    elif not content:
        message_status = "needs_input"
        response = "No usable text or transcript was present."
        failure = "Empty capture."
    elif classification == "status":
        ideas = db.scalar(select(func.count(Idea.id)).where(Idea.brand_id == brand.id)) or 0
        content_count = (
            db.scalar(select(func.count(ContentItem.id)).where(ContentItem.brand_id == brand.id))
            or 0
        )
        message_status = "completed"
        response = f"BrandOS status: {ideas} ideas and {content_count} content records."
    elif classification == "approval_request":
        message_status = "approval_required"
        response = (
            "Approval commands require the exact pending approval in the authenticated "
            "dashboard. No decision was made from this capture."
        )
    elif classification == "benchmark":
        url = next((part for part in content.split() if part.startswith("http")), None)
        if not url:
            message_status = "needs_input"
            response = "Add a full benchmark URL after /benchmark."
            failure = "Benchmark URL missing."
        else:
            benchmark = db.scalar(
                select(BenchmarkContent).where(
                    BenchmarkContent.brand_id == brand.id,
                    BenchmarkContent.source_url == url,
                )
            )
            if not benchmark:
                benchmark = BenchmarkContent(
                    brand_id=brand.id,
                    source_url=url,
                    platform="unclassified",
                    title="Telegram benchmark capture",
                    source_type="telegram_fixture" if is_simulation else "telegram",
                    raw_metadata={"acquisition": "url_only"},
                    hook_analysis="Not supplied.",
                    structure_analysis="Not supplied.",
                    visual_analysis="Not supplied.",
                    editing_analysis="Not supplied.",
                    transferable_mechanics=[],
                    protected_identity=[
                        "Do not copy exact wording, signature identity, or protected expression."
                    ],
                    mezie_adaptations=[],
                    limitations=[
                        "URL-only capture; teardown requires operator evidence.",
                        "No external acquisition was attempted.",
                    ],
                    evidence_level="url_only",
                    status="queued",
                    is_demo=is_simulation,
                )
                db.add(benchmark)
                db.flush()
            record_type = "benchmark_content"
            record_id = benchmark.id
            message_status = "completed"
            response = "Benchmark URL saved. Add evidence in Creator Benchmarks to run a teardown."
    else:
        idea_title = content.removeprefix("/idea").strip().splitlines()[0][:240]
        idea_title = idea_title or "Telegram voice idea"
        idea = Idea(
            brand_id=brand.id,
            title=idea_title,
            raw_input=content,
            source_type="telegram_simulator" if is_simulation else "telegram",
            source_reference=f"telegram:{update_id}",
            audience="Emerging Builder",
            platform_fit=[],
            is_demo=False,
        )
        db.add(idea)
        db.flush()
        record_type = "idea"
        record_id = idea.id
        message_status = "completed"
        response = f'Idea captured: "{idea.title}". Open the Ideas Inbox to score it.'

    message = TelegramMessage(
        brand_id=brand.id,
        update_id=update_id,
        sender_id=str(sender_id),
        message_id=message_id,
        message_type=message_type,
        text=text,
        transcript=transcript,
        source_reference=source_reference,
        classification=classification,
        status=message_status,
        created_record_type=record_type,
        created_record_id=record_id,
        response_text=response,
        failure_reason=failure,
        is_demo=is_simulation,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def capture_fixture(db: Session, payload: TelegramCapture) -> TelegramMessage:
    return _capture(
        db,
        update_id=f"fixture:{uuid.uuid4()}",
        sender_id=payload.sender_id,
        message_id=None,
        message_type=payload.message_type,
        text=payload.text,
        transcript=payload.transcript,
        source_reference=payload.source_reference,
        is_simulation=True,
    )


def capture_webhook_update(
    db: Session,
    settings: Settings,
    update: dict[str, Any],
    supplied_secret: str | None,
) -> TelegramMessage:
    message = update.get("message") or update.get("edited_message") or {}
    sender = message.get("from") or {}
    sender_id = sender.get("id")
    if not isinstance(sender_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Telegram update has no numeric sender ID.",
        )
    verify_webhook(settings, sender_id, supplied_secret)
    text = message.get("text") or message.get("caption")
    voice = message.get("voice")
    message_type = (
        "voice" if voice else ("link" if isinstance(text, str) and "http" in text else "text")
    )
    return _capture(
        db,
        update_id=str(update.get("update_id", "")),
        sender_id=sender_id,
        message_id=str(message.get("message_id")) if message.get("message_id") else None,
        message_type=message_type,
        text=text if isinstance(text, str) else None,
        transcript=None,
        source_reference=voice.get("file_id") if isinstance(voice, dict) else None,
        is_simulation=False,
    )
