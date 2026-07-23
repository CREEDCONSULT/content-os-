from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import Brand, MemoryRecord, SyncEvent
from app.db.session import get_db
from app.schemas.contracts import (
    MemoryRecordCreate,
    MemoryRecordView,
    MemorySearchResult,
    SyncEventView,
    VaultSyncResult,
)
from app.services.memory import (
    create_memory_record,
    initialize_vault,
    search_memory,
    sync_vault,
)

router = APIRouter(
    prefix="/api/v1/memory",
    tags=["memory"],
    dependencies=[Depends(require_user)],
)


@router.get("/records", response_model=list[MemoryRecordView])
def list_memory(db: Session = Depends(get_db)) -> list[MemoryRecord]:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        return []
    return list(
        db.scalars(
            select(MemoryRecord)
            .where(MemoryRecord.brand_id == brand_id)
            .order_by(MemoryRecord.updated_at.desc())
        ).all()
    )


@router.post(
    "/records",
    response_model=MemoryRecordView,
    status_code=status.HTTP_201_CREATED,
)
def add_memory(
    payload: MemoryRecordCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> MemoryRecord:
    return create_memory_record(db, settings, payload)


@router.get("/search", response_model=list[MemorySearchResult])
def search(
    q: str = Query(min_length=2, max_length=200),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[MemorySearchResult]:
    return search_memory(db, q, limit)


@router.post("/vault/initialize")
def initialize(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    root, created = initialize_vault(settings)
    return {"root": str(root), "initialized_folders": created}


@router.post("/vault/sync", response_model=VaultSyncResult)
def synchronize(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> VaultSyncResult:
    return sync_vault(db, settings)


@router.get("/sync-events", response_model=list[SyncEventView])
def list_sync_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[SyncEvent]:
    return list(
        db.scalars(select(SyncEvent).order_by(SyncEvent.created_at.desc()).limit(limit)).all()
    )
