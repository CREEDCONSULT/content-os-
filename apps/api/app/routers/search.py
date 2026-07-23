from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.auth import require_user
from app.db.models import (
    BenchmarkContent,
    Brand,
    BrandDocument,
    ContentItem,
    Creator,
    Idea,
    MemoryRecord,
)
from app.db.session import get_db
from app.schemas.contracts import GlobalSearchResult

router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
    dependencies=[Depends(require_user)],
)


def _score(title: str, query: str, authority: str) -> float:
    normalized_title = title.lower()
    normalized_query = query.lower()
    exact = 8 if normalized_title == normalized_query else 0
    prefix = 4 if normalized_title.startswith(normalized_query) else 0
    contains = normalized_title.count(normalized_query) * 2
    authority_bonus = 3 if authority == "canonical" else 1
    return float(exact + prefix + contains + authority_bonus)


@router.get("", response_model=list[GlobalSearchResult])
def global_search(
    q: str = Query(min_length=2, max_length=200),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[GlobalSearchResult]:
    brand_id = db.scalar(select(Brand.id).where(Brand.is_active.is_(True)))
    if not brand_id:
        return []
    pattern = f"%{q}%"
    results: list[GlobalSearchResult] = []

    documents = db.scalars(
        select(BrandDocument)
        .where(
            BrandDocument.brand_id == brand_id,
            BrandDocument.title.ilike(pattern),
        )
        .limit(limit)
    )
    for item in documents:
        authority = item.canonical_status.value
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="brand_document",
                title=item.title,
                excerpt=f"{item.document_type} · {item.source_path or 'database'}",
                href="/brand",
                authority=authority,
                score=_score(item.title, q, authority),
                is_demo=False,
            )
        )

    ideas = db.scalars(
        select(Idea)
        .where(
            Idea.brand_id == brand_id,
            or_(Idea.title.ilike(pattern), Idea.raw_input.ilike(pattern)),
        )
        .limit(limit)
    )
    for item in ideas:
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="idea",
                title=item.title,
                excerpt=item.raw_input[:220],
                href="/ideas",
                authority=item.status.value,
                score=_score(item.title, q, item.status.value),
                is_demo=item.is_demo,
            )
        )

    content = db.scalars(
        select(ContentItem)
        .where(
            ContentItem.brand_id == brand_id,
            or_(ContentItem.title.ilike(pattern), ContentItem.objective.ilike(pattern)),
        )
        .limit(limit)
    )
    for item in content:
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="content_item",
                title=item.title,
                excerpt=f"{item.platform} · {item.format} · {item.objective}",
                href="/pipeline",
                authority=item.status.value,
                score=_score(item.title, q, item.status.value),
                is_demo=item.is_demo,
            )
        )

    memories = db.scalars(
        select(MemoryRecord)
        .where(
            MemoryRecord.brand_id == brand_id,
            MemoryRecord.sensitivity != "restricted",
            or_(MemoryRecord.title.ilike(pattern), MemoryRecord.content.ilike(pattern)),
        )
        .limit(limit)
    )
    for item in memories:
        authority = item.canonical_status.value
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="memory",
                title=item.title,
                excerpt=f"{item.memory_type} · {item.vault_path}",
                href="/intelligence",
                authority=authority,
                score=_score(item.title, q, authority) + item.confidence,
                is_demo=item.is_demo,
            )
        )

    creators = db.scalars(
        select(Creator)
        .where(
            Creator.brand_id == brand_id,
            or_(Creator.name.ilike(pattern), Creator.username.ilike(pattern)),
        )
        .limit(limit)
    )
    for item in creators:
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="creator",
                title=item.name,
                excerpt=f"{item.platform} · Tier {item.tier} · {item.why_tracked[:160]}",
                href="/benchmarks",
                authority="watchlist",
                score=_score(item.name, q, "watchlist") + item.relevance_score / 10,
                is_demo=item.is_demo,
            )
        )

    benchmarks = db.scalars(
        select(BenchmarkContent)
        .where(
            BenchmarkContent.brand_id == brand_id,
            BenchmarkContent.title.ilike(pattern),
        )
        .limit(limit)
    )
    for item in benchmarks:
        results.append(
            GlobalSearchResult(
                id=item.id,
                record_type="benchmark",
                title=item.title,
                excerpt=f"{item.platform} · {item.evidence_level}",
                href="/benchmarks",
                authority=item.evidence_level,
                score=_score(item.title, q, item.evidence_level),
                is_demo=item.is_demo,
            )
        )

    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
