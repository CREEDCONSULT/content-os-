from __future__ import annotations

import hashlib

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Approval,
    ApprovalStatus,
    BrandDocument,
    BrandDocumentVersion,
    CanonicalStatus,
    RiskLevel,
)


def active_version(db: Session, document: BrandDocument) -> BrandDocumentVersion | None:
    if not document.current_version_id:
        return None
    return db.get(BrandDocumentVersion, document.current_version_id)


def create_version(
    db: Session,
    document: BrandDocument,
    content: str,
    change_summary: str,
    actor: str,
) -> tuple[BrandDocumentVersion, Approval | None, bool]:
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    existing = db.scalar(
        select(BrandDocumentVersion).where(
            BrandDocumentVersion.brand_document_id == document.id,
            BrandDocumentVersion.checksum_sha256 == checksum,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This version already exists."
        )

    version = BrandDocumentVersion(
        brand_document_id=document.id,
        version_number=document.version_count + 1,
        content_markdown=content,
        change_summary=change_summary,
        checksum_sha256=checksum,
        provenance={"source": "dashboard", "actor": actor},
        created_by=actor,
        is_active=False,
    )
    db.add(version)
    db.flush()
    document.version_count += 1

    approval: Approval | None = None
    activated = document.canonical_status != CanonicalStatus.CANONICAL
    if activated:
        current = active_version(db, document)
        if current:
            current.is_active = False
        version.is_active = True
        document.current_version_id = version.id
    else:
        approval = Approval(
            brand_id=document.brand_id,
            action_type="canonical_brand_change",
            target_type="brand_document",
            target_id=document.id,
            requested_by=actor,
            risk_level=RiskLevel.HIGH,
            status=ApprovalStatus.PENDING,
            context={
                "proposed_version_id": version.id,
                "version_number": version.version_number,
                "change_summary": change_summary,
            },
        )
        db.add(approval)
        db.flush()
        version.approval_id = approval.id

    db.commit()
    db.refresh(version)
    if approval:
        db.refresh(approval)
    return version, approval, activated
