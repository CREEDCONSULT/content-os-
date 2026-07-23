from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal, require_user
from app.db.models import Approval, ApprovalStatus
from app.db.session import get_db
from app.schemas.contracts import ApprovalDecision, ApprovalView
from app.services.approvals import decide_approval

router = APIRouter(
    prefix="/api/v1/approvals", tags=["approvals"], dependencies=[Depends(require_user)]
)


@router.get("", response_model=list[ApprovalView])
def list_approvals(
    approval_status: ApprovalStatus | None = Query(default=ApprovalStatus.PENDING, alias="status"),
    db: Session = Depends(get_db),
) -> list[Approval]:
    statement = select(Approval)
    if approval_status:
        statement = statement.where(Approval.status == approval_status)
    return list(db.scalars(statement.order_by(Approval.created_at.desc())).all())


@router.post("/{approval_id}/decision", response_model=ApprovalView)
def decide(
    approval_id: str,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    user: UserPrincipal = Depends(require_user),
) -> Approval:
    approval = db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found.")
    decision = (
        ApprovalStatus.APPROVED if payload.decision == "approved" else ApprovalStatus.REJECTED
    )
    return decide_approval(db, approval, decision, user.username, payload.notes)
