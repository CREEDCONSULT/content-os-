from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.db.models import Brand, ProofItem
from app.db.session import get_db
from app.schemas.contracts import ProofItemCreate, ProofItemView
from app.services.proof import create_proof_item

router = APIRouter(
    prefix="/api/v1/proof",
    tags=["proof"],
    dependencies=[Depends(require_user)],
)


@router.get("", response_model=list[ProofItemView])
def list_proof(db: Session = Depends(get_db)) -> list[ProofItem]:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(ProofItem)
            .where(ProofItem.brand_id == brand_id)
            .order_by(ProofItem.updated_at.desc())
        ).all()
    )


@router.post("", response_model=ProofItemView, status_code=status.HTTP_201_CREATED)
def add_proof(
    payload: ProofItemCreate,
    db: Session = Depends(get_db),
) -> ProofItem:
    return create_proof_item(db, payload)
