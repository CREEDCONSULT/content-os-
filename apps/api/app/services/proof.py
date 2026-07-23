from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Asset, Brand, ContentItem, ProofItem, ProofStatus
from app.schemas.contracts import ProofItemCreate


def create_proof_item(db: Session, payload: ProofItemCreate) -> ProofItem:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    if payload.content_item_id and not db.get(ContentItem, payload.content_item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked content item not found.",
        )
    missing_assets = [asset_id for asset_id in payload.asset_ids if not db.get(Asset, asset_id)]
    if missing_assets:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="One or more linked assets do not exist.",
        )
    permission_ok = (
        payload.sensitivity != "client_confidential" or payload.permission_status == "approved"
    )
    status_value = (
        ProofStatus.VERIFIED
        if payload.evidence_links and permission_ok
        else ProofStatus.EVIDENCE_NEEDED
    )
    proof = ProofItem(
        brand_id=brand.id,
        **payload.model_dump(),
        status=status_value,
        is_demo=False,
    )
    db.add(proof)
    db.commit()
    db.refresh(proof)
    return proof
