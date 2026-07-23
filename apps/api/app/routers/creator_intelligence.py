from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import BenchmarkContent, Brand, Creator
from app.db.session import get_db
from app.schemas.contracts import (
    BenchmarkCreate,
    BenchmarkView,
    CreatorCreate,
    CreatorView,
)
from app.services.intelligence import create_benchmark, create_creator

router = APIRouter(
    prefix="/api/v1/intelligence",
    tags=["creator-intelligence"],
    dependencies=[Depends(require_user)],
)


def _brand_id(db: Session) -> str | None:
    return db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))


@router.get("/creators", response_model=list[CreatorView])
def list_creators(db: Session = Depends(get_db)) -> list[Creator]:
    brand_id = _brand_id(db)
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(Creator)
            .where(Creator.brand_id == brand_id)
            .order_by(Creator.tier, Creator.relevance_score.desc())
        ).all()
    )


@router.post(
    "/creators",
    response_model=CreatorView,
    status_code=status.HTTP_201_CREATED,
)
def add_creator(
    payload: CreatorCreate,
    db: Session = Depends(get_db),
) -> Creator:
    return create_creator(db, payload)


@router.get("/benchmarks", response_model=list[BenchmarkView])
def list_benchmarks(db: Session = Depends(get_db)) -> list[BenchmarkContent]:
    brand_id = _brand_id(db)
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(BenchmarkContent)
            .where(BenchmarkContent.brand_id == brand_id)
            .order_by(BenchmarkContent.updated_at.desc())
        ).all()
    )


@router.post(
    "/benchmarks",
    response_model=BenchmarkView,
    status_code=status.HTTP_201_CREATED,
)
def add_benchmark(
    payload: BenchmarkCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BenchmarkContent:
    return create_benchmark(db, payload, settings)
