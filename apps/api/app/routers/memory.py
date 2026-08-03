from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.db.models import Brand, MemoryRecord, SyncEvent
from app.db.session import get_db
from app.schemas.contracts import (
    KnowledgeEdgeCreate,
    KnowledgeEdgeView,
    KnowledgeEntityCreate,
    KnowledgeEntityView,
    MemoryGraphExtractionResult,
    MemoryGraphNeighborhood,
    MemoryGraphSearchResult,
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
from app.services.memory_graph import (
    build_memory_graph,
    create_knowledge_edge,
    create_knowledge_entity,
    get_knowledge_entity,
    graph_conflicts,
    graph_neighborhood,
    graph_pending_approvals,
    graph_search,
    list_knowledge_edges,
    list_knowledge_entities,
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


@router.get("/entities", response_model=list[KnowledgeEntityView])
def list_entities(
    entity_type: str | None = Query(default=None, min_length=2, max_length=80),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return list_knowledge_entities(db, entity_type, limit)


@router.post(
    "/entities",
    response_model=KnowledgeEntityView,
    status_code=status.HTTP_201_CREATED,
)
def add_entity(payload: KnowledgeEntityCreate, db: Session = Depends(get_db)):
    return create_knowledge_entity(db, payload)


@router.get("/entities/{entity_id}", response_model=KnowledgeEntityView)
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    return get_knowledge_entity(db, entity_id)


@router.get("/edges", response_model=list[KnowledgeEdgeView])
def list_edges(
    source_type: str | None = Query(default=None, min_length=2, max_length=80),
    source_id: str | None = Query(default=None, min_length=1, max_length=120),
    target_type: str | None = Query(default=None, min_length=2, max_length=80),
    target_id: str | None = Query(default=None, min_length=1, max_length=120),
    relationship_type: str | None = Query(default=None, min_length=2, max_length=80),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_knowledge_edges(
        db,
        source_type,
        source_id,
        target_type,
        target_id,
        relationship_type,
        limit,
    )


@router.post(
    "/edges",
    response_model=KnowledgeEdgeView,
    status_code=status.HTTP_201_CREATED,
)
def add_edge(payload: KnowledgeEdgeCreate, db: Session = Depends(get_db)):
    return create_knowledge_edge(db, payload)


@router.post("/graph/extract", response_model=MemoryGraphExtractionResult)
def extract_graph(db: Session = Depends(get_db)) -> MemoryGraphExtractionResult:
    return build_memory_graph(db)


@router.get("/graph/neighborhood", response_model=MemoryGraphNeighborhood)
def get_graph_neighborhood(
    node_type: str = Query(min_length=2, max_length=80),
    node_id: str = Query(min_length=1, max_length=120),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> MemoryGraphNeighborhood:
    return graph_neighborhood(db, node_type, node_id, limit)


@router.get("/graph/search", response_model=list[MemoryGraphSearchResult])
def search_graph(
    q: str = Query(min_length=2, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[MemoryGraphSearchResult]:
    return graph_search(db, q, limit)


@router.get("/graph/conflicts", response_model=list[KnowledgeEdgeView])
def list_graph_conflicts(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return graph_conflicts(db, limit)


@router.get("/graph/pending-approvals", response_model=list[KnowledgeEdgeView])
def list_graph_pending_approvals(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return graph_pending_approvals(db, limit)


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
