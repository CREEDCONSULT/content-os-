from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Approval, ApprovalStatus, BrandDocument, BrandDocumentVersion


def decide_approval(
    db: Session,
    approval: Approval,
    decision: ApprovalStatus,
    actor: str,
    notes: str | None,
) -> Approval:
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval is already {approval.status.value}.",
        )

    if decision not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid decision."
        )

    if decision == ApprovalStatus.APPROVED and approval.action_type == "canonical_brand_change":
        document = db.get(BrandDocument, approval.target_id)
        version_id = approval.context.get("proposed_version_id")
        version = db.get(BrandDocumentVersion, version_id) if version_id else None
        if not document or not version or version.brand_document_id != document.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Proposed canonical version is unavailable.",
            )
        current = db.scalar(
            select(BrandDocumentVersion).where(
                BrandDocumentVersion.brand_document_id == document.id,
                BrandDocumentVersion.is_active.is_(True),
            )
        )
        if current:
            current.is_active = False
        version.is_active = True
        document.current_version_id = version.id

    approval.status = decision
    approval.approved_by = actor
    approval.decided_at = datetime.now(UTC)
    approval.notes = notes
    db.commit()
    db.refresh(approval)
    return approval
