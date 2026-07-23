from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pipeline import ALLOWED_TRANSITIONS
from app.db.models import (
    Approval,
    ApprovalStatus,
    ContentItem,
    PipelineEvent,
    PipelineStatus,
)


def transition_content(
    db: Session,
    item: ContentItem,
    target: PipelineStatus,
    actor: str,
    reason: str | None,
) -> ContentItem:
    allowed = ALLOWED_TRANSITIONS[item.status]
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot move content from {item.status.value} to {target.value}.",
        )

    if target == PipelineStatus.PUBLISHED:
        approval = db.scalar(
            select(Approval).where(
                Approval.target_type == "content_item",
                Approval.target_id == item.id,
                Approval.action_type == "publish_content",
                Approval.status == ApprovalStatus.APPROVED,
            )
        )
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Publishing requires an approved backend approval record.",
            )

    if (
        target in {PipelineStatus.APPROVED, PipelineStatus.READY_TO_SHOOT}
        and not item.is_demo
        and item.approval_status != ApprovalStatus.APPROVED
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A final script approval is required before production.",
        )

    event = PipelineEvent(
        content_item_id=item.id,
        from_status=item.status.value,
        to_status=target.value,
        actor=actor,
        reason=reason,
    )
    item.status = target
    db.add(event)
    db.commit()
    db.refresh(item)
    return item
