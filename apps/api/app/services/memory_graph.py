from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    Asset,
    BenchmarkContent,
    Brand,
    BrandDocument,
    CanonicalStatus,
    ContentBrief,
    ContentItem,
    Creator,
    Experiment,
    Idea,
    KnowledgeEdge,
    KnowledgeEntity,
    MemoryRecord,
    MetricSnapshot,
    ProductionPlan,
    ProofItem,
    Script,
    utc_now,
)
from app.schemas.contracts import (
    GraphRelatedNode,
    KnowledgeEdgeCreate,
    KnowledgeEntityCreate,
    MemoryGraphExtractionResult,
    MemoryGraphNeighborhood,
    MemoryGraphSearchResult,
)

PILLARS = ("Build", "Leverage", "Own", "Lead", "See", "Create")
PLATFORMS = ("LinkedIn", "Instagram", "TikTok", "YouTube", "X", "Newsletter")
KNOWN_REFERENCES: tuple[tuple[str, str, str], ...] = (
    ("project", "BrandOS", "belongs_to"),
    ("project", "CreedAI", "references_external"),
    ("brand", "Creed Consult", "references_external"),
    ("brand", "Mezie", "belongs_to"),
    ("person", "Mr. C. Mezie", "belongs_to"),
)


@dataclass
class GraphBuildStats:
    entities_created: int = 0
    entities_reused: int = 0
    edges_created: int = 0
    edges_reused: int = 0


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def _clean_type(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Graph node and relationship types must contain letters or numbers.",
        )
    return cleaned[:80]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:240] or "entity"


def _node_type(value: str) -> str:
    cleaned = _clean_type(value)
    if cleaned == "entity":
        return "knowledge_entity"
    return cleaned


def create_knowledge_entity(
    db: Session,
    payload: KnowledgeEntityCreate,
) -> KnowledgeEntity:
    brand = _active_brand(db)
    entity_type = _clean_type(payload.entity_type)
    slug = _slugify(payload.slug or payload.name)
    existing = db.scalar(
        select(KnowledgeEntity).where(
            KnowledgeEntity.brand_id == brand.id,
            KnowledgeEntity.entity_type == entity_type,
            KnowledgeEntity.slug == slug,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A knowledge entity already owns this type and slug.",
        )
    entity = KnowledgeEntity(
        brand_id=brand.id,
        entity_type=entity_type,
        name=payload.name,
        slug=slug,
        description=payload.description,
        aliases=payload.aliases,
        canonical_status=payload.canonical_status,
        sensitivity=payload.sensitivity,
        confidence=payload.confidence,
        provenance=payload.provenance or {"source": "manual"},
        first_seen_at=utc_now(),
        last_seen_at=utc_now(),
        is_demo=payload.is_demo,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def create_knowledge_edge(
    db: Session,
    payload: KnowledgeEdgeCreate,
) -> KnowledgeEdge:
    brand = _active_brand(db)
    source_type = _node_type(payload.source_type)
    target_type = _node_type(payload.target_type)
    relationship_type = _clean_type(payload.relationship_type)
    existing = db.scalar(
        select(KnowledgeEdge).where(
            KnowledgeEdge.brand_id == brand.id,
            KnowledgeEdge.source_type == source_type,
            KnowledgeEdge.source_id == payload.source_id,
            KnowledgeEdge.relationship_type == relationship_type,
            KnowledgeEdge.target_type == target_type,
            KnowledgeEdge.target_id == payload.target_id,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A knowledge edge already connects these nodes with this relationship.",
        )
    edge = KnowledgeEdge(
        brand_id=brand.id,
        source_type=source_type,
        source_id=payload.source_id,
        target_type=target_type,
        target_id=payload.target_id,
        relationship_type=relationship_type,
        label=payload.label or f"{source_type} {relationship_type} {target_type}",
        evidence=payload.evidence,
        confidence=payload.confidence,
        canonical_status=payload.canonical_status,
        sensitivity=payload.sensitivity,
        provenance=payload.provenance or {"source": "manual"},
        created_by=payload.created_by,
        is_demo=payload.is_demo,
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


def list_knowledge_entities(
    db: Session,
    entity_type: str | None,
    limit: int,
) -> list[KnowledgeEntity]:
    brand = _active_brand(db)
    statement = select(KnowledgeEntity).where(KnowledgeEntity.brand_id == brand.id)
    if entity_type:
        statement = statement.where(KnowledgeEntity.entity_type == _clean_type(entity_type))
    return list(
        db.scalars(
            statement.order_by(KnowledgeEntity.updated_at.desc(), KnowledgeEntity.name).limit(limit)
        ).all()
    )


def get_knowledge_entity(db: Session, entity_id: str) -> KnowledgeEntity:
    brand = _active_brand(db)
    entity = db.get(KnowledgeEntity, entity_id)
    if not entity or entity.brand_id != brand.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.")
    return entity


def list_knowledge_edges(
    db: Session,
    source_type: str | None,
    source_id: str | None,
    target_type: str | None,
    target_id: str | None,
    relationship_type: str | None,
    limit: int,
) -> list[KnowledgeEdge]:
    brand = _active_brand(db)
    statement = select(KnowledgeEdge).where(KnowledgeEdge.brand_id == brand.id)
    if source_type:
        statement = statement.where(KnowledgeEdge.source_type == _node_type(source_type))
    if source_id:
        statement = statement.where(KnowledgeEdge.source_id == source_id)
    if target_type:
        statement = statement.where(KnowledgeEdge.target_type == _node_type(target_type))
    if target_id:
        statement = statement.where(KnowledgeEdge.target_id == target_id)
    if relationship_type:
        statement = statement.where(
            KnowledgeEdge.relationship_type == _clean_type(relationship_type)
        )
    return list(
        db.scalars(
            statement.order_by(KnowledgeEdge.updated_at.desc(), KnowledgeEdge.id).limit(limit)
        ).all()
    )


def _entity(
    db: Session,
    brand_id: str,
    entity_type: str,
    name: str,
    stats: GraphBuildStats,
    *,
    aliases: list[str] | None = None,
    description: str = "",
    provenance: dict[str, Any] | None = None,
    confidence: float = 0.8,
    is_demo: bool = False,
) -> KnowledgeEntity:
    normalized_type = _clean_type(entity_type)
    slug = _slugify(name)
    existing = db.scalar(
        select(KnowledgeEntity).where(
            KnowledgeEntity.brand_id == brand_id,
            KnowledgeEntity.entity_type == normalized_type,
            KnowledgeEntity.slug == slug,
        )
    )
    now = utc_now()
    if existing:
        existing.last_seen_at = now
        existing.confidence = max(existing.confidence, confidence)
        stats.entities_reused += 1
        return existing

    entity = KnowledgeEntity(
        brand_id=brand_id,
        entity_type=normalized_type,
        name=name,
        slug=slug,
        description=description,
        aliases=aliases or [],
        canonical_status=CanonicalStatus.CANONICAL,
        sensitivity="internal",
        confidence=confidence,
        provenance=provenance or {"source": "deterministic_graph_builder"},
        first_seen_at=now,
        last_seen_at=now,
        is_demo=is_demo,
    )
    db.add(entity)
    db.flush()
    stats.entities_created += 1
    return entity


def _edge(
    db: Session,
    brand_id: str,
    source_type: str,
    source_id: str,
    relationship_type: str,
    target_type: str,
    target_id: str,
    stats: GraphBuildStats,
    *,
    label: str,
    evidence: list[dict[str, Any]] | None = None,
    provenance: dict[str, Any] | None = None,
    confidence: float = 0.8,
    canonical_status: CanonicalStatus = CanonicalStatus.CANONICAL,
    sensitivity: str = "internal",
    is_demo: bool = False,
) -> KnowledgeEdge:
    normalized_source = _node_type(source_type)
    normalized_target = _node_type(target_type)
    normalized_relationship = _clean_type(relationship_type)
    existing = db.scalar(
        select(KnowledgeEdge).where(
            KnowledgeEdge.brand_id == brand_id,
            KnowledgeEdge.source_type == normalized_source,
            KnowledgeEdge.source_id == source_id,
            KnowledgeEdge.relationship_type == normalized_relationship,
            KnowledgeEdge.target_type == normalized_target,
            KnowledgeEdge.target_id == target_id,
        )
    )
    if existing:
        existing.confidence = max(existing.confidence, confidence)
        stats.edges_reused += 1
        return existing

    edge = KnowledgeEdge(
        brand_id=brand_id,
        source_type=normalized_source,
        source_id=source_id,
        target_type=normalized_target,
        target_id=target_id,
        relationship_type=normalized_relationship,
        label=label,
        evidence=evidence or [],
        confidence=confidence,
        canonical_status=canonical_status,
        sensitivity=sensitivity,
        provenance=provenance or {"source": "deterministic_graph_builder"},
        created_by="system",
        is_demo=is_demo,
    )
    db.add(edge)
    db.flush()
    stats.edges_created += 1
    return edge


def _edge_to_entity(
    db: Session,
    brand_id: str,
    source_type: str,
    source_id: str,
    relationship_type: str,
    entity_type: str,
    entity_name: str,
    stats: GraphBuildStats,
    *,
    evidence: list[dict[str, Any]] | None = None,
    confidence: float = 0.8,
    is_demo: bool = False,
) -> None:
    target = _entity(
        db,
        brand_id,
        entity_type,
        entity_name,
        stats,
        provenance={"source": "structured_field", "field_value": entity_name},
        confidence=confidence,
        is_demo=is_demo,
    )
    _edge(
        db,
        brand_id,
        source_type,
        source_id,
        relationship_type,
        "knowledge_entity",
        target.id,
        stats,
        label=f"{source_type} {relationship_type} {entity_name}",
        evidence=evidence,
        confidence=confidence,
        is_demo=is_demo,
    )


def _textual_entities(text: str) -> list[tuple[str, str, str]]:
    corpus = text.lower()
    found: list[tuple[str, str, str]] = []
    for platform in PLATFORMS:
        if re.search(rf"\b{re.escape(platform.lower())}\b", corpus):
            found.append(("platform", platform, "belongs_to"))
    for pillar in PILLARS:
        if re.search(rf"\b{re.escape(pillar.lower())}\b", corpus):
            found.append(("content_pillar", pillar, "expresses"))
    for entity_type, name, relationship in KNOWN_REFERENCES:
        if name.lower() in corpus:
            found.append((entity_type, name, relationship))
    return found


def _vault_area(vault_path: str) -> str | None:
    parts = vault_path.replace("\\", "/").split("/")
    if not parts or not parts[0]:
        return None
    return parts[0].replace("_", " ")


def _link_structured_context(
    db: Session,
    brand_id: str,
    source_type: str,
    source_id: str,
    stats: GraphBuildStats,
    *,
    pillar: str | None = None,
    audience: str | None = None,
    platform: str | None = None,
    platforms: list[str] | None = None,
    is_demo: bool = False,
) -> None:
    if pillar:
        _edge_to_entity(
            db,
            brand_id,
            source_type,
            source_id,
            "expresses",
            "content_pillar",
            pillar,
            stats,
            evidence=[{"source": "structured_field", "field": "pillar"}],
            is_demo=is_demo,
        )
    if audience:
        _edge_to_entity(
            db,
            brand_id,
            source_type,
            source_id,
            "targets",
            "audience_segment",
            audience,
            stats,
            evidence=[{"source": "structured_field", "field": "audience"}],
            is_demo=is_demo,
        )
    platform_values = [platform] if platform else []
    platform_values.extend(platforms or [])
    for value in {item for item in platform_values if item}:
        _edge_to_entity(
            db,
            brand_id,
            source_type,
            source_id,
            "belongs_to",
            "platform",
            value,
            stats,
            evidence=[{"source": "structured_field", "field": "platform"}],
            is_demo=is_demo,
        )


def build_memory_graph(db: Session) -> MemoryGraphExtractionResult:
    brand = _active_brand(db)
    stats = GraphBuildStats()

    _entity(
        db,
        brand.id,
        "brand",
        brand.name,
        stats,
        aliases=["Mezie", "Mr. C. Mezie"],
        description=brand.positioning,
        provenance={"source": "active_brand"},
        confidence=1,
    )
    _entity(
        db,
        brand.id,
        "person",
        brand.founder_name,
        stats,
        provenance={"source": "active_brand", "field": "founder_name"},
        confidence=1,
    )

    for record in db.scalars(select(MemoryRecord).where(MemoryRecord.brand_id == brand.id)).all():
        if record.sensitivity == "restricted" or record.sync_status == "conflict":
            continue
        source = ("memory_record", record.id)
        area = _vault_area(record.vault_path)
        if area:
            _edge_to_entity(
                db,
                brand.id,
                source[0],
                source[1],
                "belongs_to",
                "source",
                f"Vault area: {area}",
                stats,
                evidence=[{"source": "vault_path", "path": record.vault_path}],
                confidence=0.95,
                is_demo=record.is_demo,
            )
        for entity_type, name, relationship in _textual_entities(
            f"{record.title}\n{record.content}\n{record.vault_path}"
        ):
            _edge_to_entity(
                db,
                brand.id,
                source[0],
                source[1],
                relationship,
                entity_type,
                name,
                stats,
                evidence=[{"source": "deterministic_text_match", "record": record.vault_path}],
                confidence=0.65,
                is_demo=record.is_demo,
            )

    for document in db.scalars(
        select(BrandDocument).where(BrandDocument.brand_id == brand.id)
    ).all():
        source_entity = _entity(
            db,
            brand.id,
            "source",
            document.title,
            stats,
            description=document.document_type,
            provenance={
                "source": "brand_document",
                "document_id": document.id,
                "source_path": document.source_path,
            },
            confidence=0.9,
        )
        _edge(
            db,
            brand.id,
            "brand_document",
            document.id,
            "derived_from",
            "knowledge_entity",
            source_entity.id,
            stats,
            label=f"brand_document derived_from {document.title}",
            evidence=[{"source_path": document.source_path, "vault_path": document.vault_path}],
            confidence=0.9,
            canonical_status=document.canonical_status,
        )

    for idea in db.scalars(select(Idea).where(Idea.brand_id == brand.id)).all():
        _link_structured_context(
            db,
            brand.id,
            "idea",
            idea.id,
            stats,
            pillar=idea.pillar,
            audience=idea.audience,
            platforms=idea.platform_fit,
            is_demo=idea.is_demo,
        )
        if idea.source_reference and idea.source_reference.startswith("vault:"):
            vault_path = idea.source_reference.removeprefix("vault:")
            memory = db.scalar(
                select(MemoryRecord).where(
                    MemoryRecord.brand_id == brand.id,
                    MemoryRecord.vault_path == vault_path,
                )
            )
            if memory:
                _edge(
                    db,
                    brand.id,
                    "idea",
                    idea.id,
                    "derived_from",
                    "memory_record",
                    memory.id,
                    stats,
                    label=f"idea derived_from {memory.title}",
                    evidence=[{"source_reference": idea.source_reference}],
                    confidence=0.95,
                    is_demo=idea.is_demo,
                )

    for item in db.scalars(select(ContentItem).where(ContentItem.brand_id == brand.id)).all():
        _link_structured_context(
            db,
            brand.id,
            "content_item",
            item.id,
            stats,
            pillar=item.pillar,
            audience=item.audience,
            platform=item.platform,
            is_demo=item.is_demo,
        )
        if item.idea_id:
            _edge(
                db,
                brand.id,
                "content_item",
                item.id,
                "derived_from",
                "idea",
                item.idea_id,
                stats,
                label=f"content_item derived_from idea {item.idea_id}",
                confidence=0.95,
                is_demo=item.is_demo,
            )

    for brief in db.scalars(select(ContentBrief).where(ContentBrief.brand_id == brand.id)).all():
        _link_structured_context(
            db,
            brand.id,
            "content_brief",
            brief.id,
            stats,
            pillar=brief.pillar,
            audience=brief.audience,
            platform=brief.platform,
            is_demo=brief.is_demo,
        )
        _edge(
            db,
            brand.id,
            "idea",
            brief.idea_id,
            "became_brief",
            "content_brief",
            brief.id,
            stats,
            label=f"idea became_brief {brief.title}",
            confidence=0.98,
            is_demo=brief.is_demo,
        )
        _edge(
            db,
            brand.id,
            "content_brief",
            brief.id,
            "belongs_to",
            "content_item",
            brief.content_item_id,
            stats,
            label=f"content_brief belongs_to content_item {brief.content_item_id}",
            confidence=0.98,
            is_demo=brief.is_demo,
        )

    for script in db.scalars(select(Script).where(Script.brand_id == brand.id)).all():
        _edge(
            db,
            brand.id,
            "content_brief",
            script.content_brief_id,
            "became_script",
            "script",
            script.id,
            stats,
            label=f"content_brief became_script {script.title}",
            confidence=0.98,
            is_demo=script.is_demo,
        )
        _edge(
            db,
            brand.id,
            "script",
            script.id,
            "belongs_to",
            "content_item",
            script.content_item_id,
            stats,
            label=f"script belongs_to content_item {script.content_item_id}",
            confidence=0.98,
            is_demo=script.is_demo,
        )

    for plan in db.scalars(select(ProductionPlan).where(ProductionPlan.brand_id == brand.id)).all():
        _edge(
            db,
            brand.id,
            "script",
            plan.script_id,
            "became_shoot_plan",
            "production_plan",
            plan.id,
            stats,
            label=f"script became_shoot_plan {plan.title}",
            confidence=0.98,
            is_demo=plan.is_demo,
        )
        _edge(
            db,
            brand.id,
            "production_plan",
            plan.id,
            "belongs_to",
            "content_item",
            plan.content_item_id,
            stats,
            label=f"production_plan belongs_to content_item {plan.content_item_id}",
            confidence=0.98,
            is_demo=plan.is_demo,
        )

    for asset in db.scalars(select(Asset).where(Asset.brand_id == brand.id)).all():
        if asset.content_item_id:
            _edge(
                db,
                brand.id,
                "content_item",
                asset.content_item_id,
                "uses_asset",
                "asset",
                asset.id,
                stats,
                label=f"content_item uses_asset {asset.filename}",
                evidence=[{"checksum_sha256": asset.checksum_sha256}],
                confidence=0.98,
                is_demo=asset.is_demo,
            )
        if asset.production_plan_id:
            _edge(
                db,
                brand.id,
                "production_plan",
                asset.production_plan_id,
                "uses_asset",
                "asset",
                asset.id,
                stats,
                label=f"production_plan uses_asset {asset.filename}",
                evidence=[{"checksum_sha256": asset.checksum_sha256}],
                confidence=0.98,
                is_demo=asset.is_demo,
            )

    for proof in db.scalars(select(ProofItem).where(ProofItem.brand_id == brand.id)).all():
        if proof.content_item_id:
            _edge(
                db,
                brand.id,
                "proof_item",
                proof.id,
                "supports",
                "content_item",
                proof.content_item_id,
                stats,
                label=f"proof_item supports content_item {proof.content_item_id}",
                evidence=proof.evidence_links,
                confidence=0.85,
                sensitivity=proof.sensitivity,
                is_demo=proof.is_demo,
            )

    for creator in db.scalars(select(Creator).where(Creator.brand_id == brand.id)).all():
        _edge_to_entity(
            db,
            brand.id,
            "creator",
            creator.id,
            "belongs_to",
            "platform",
            creator.platform,
            stats,
            evidence=[{"source": "creator.platform"}],
            confidence=0.95,
            is_demo=creator.is_demo,
        )
        for pillar in creator.content_pillars:
            _edge_to_entity(
                db,
                brand.id,
                "creator",
                creator.id,
                "expresses",
                "content_pillar",
                pillar,
                stats,
                evidence=[{"source": "creator.content_pillars"}],
                confidence=0.75,
                is_demo=creator.is_demo,
            )

    for benchmark in db.scalars(
        select(BenchmarkContent).where(BenchmarkContent.brand_id == brand.id)
    ).all():
        _edge_to_entity(
            db,
            brand.id,
            "benchmark_content",
            benchmark.id,
            "belongs_to",
            "platform",
            benchmark.platform,
            stats,
            evidence=[{"source": "benchmark.platform"}],
            confidence=0.95,
            is_demo=benchmark.is_demo,
        )
        if benchmark.creator_id:
            _edge(
                db,
                brand.id,
                "benchmark_content",
                benchmark.id,
                "derived_from",
                "creator",
                benchmark.creator_id,
                stats,
                label=f"benchmark_content derived_from creator {benchmark.creator_id}",
                confidence=0.9,
                is_demo=benchmark.is_demo,
            )

    for metric in db.scalars(
        select(MetricSnapshot).where(MetricSnapshot.brand_id == brand.id)
    ).all():
        if metric.content_item_id:
            _edge(
                db,
                brand.id,
                "content_item",
                metric.content_item_id,
                "performed_with",
                "metric_snapshot",
                metric.id,
                stats,
                label=f"content_item performed_with {metric.platform} metric snapshot",
                evidence=[
                    {
                        "views": metric.views,
                        "impressions": metric.impressions,
                        "engagement": metric.engagement,
                        "saves": metric.saves,
                        "shares": metric.shares,
                    }
                ],
                confidence=0.95,
                is_demo=metric.is_demo,
            )

    for experiment in db.scalars(select(Experiment).where(Experiment.brand_id == brand.id)).all():
        _edge_to_entity(
            db,
            brand.id,
            "experiment",
            experiment.id,
            "belongs_to",
            "platform",
            experiment.platform,
            stats,
            evidence=[{"source": "experiment.platform"}],
            confidence=0.9,
            is_demo=experiment.is_demo,
        )

    db.commit()
    total_entities = db.scalar(
        select(func.count())
        .select_from(KnowledgeEntity)
        .where(KnowledgeEntity.brand_id == brand.id)
    )
    total_edges = db.scalar(
        select(func.count()).select_from(KnowledgeEdge).where(KnowledgeEdge.brand_id == brand.id)
    )
    return MemoryGraphExtractionResult(
        brand_id=brand.id,
        entities_created=stats.entities_created,
        entities_reused=stats.entities_reused,
        edges_created=stats.edges_created,
        edges_reused=stats.edges_reused,
        totals={
            "knowledge_entities": int(total_entities or 0),
            "knowledge_edges": int(total_edges or 0),
        },
        notes=[
            "Built deterministic graph edges from structured BrandOS records.",
            "AI extraction and embeddings are intentionally not required for this pass.",
        ],
    )


def _describe_node(db: Session, node_type: str, node_id: str) -> GraphRelatedNode:
    normalized = _node_type(node_type)
    model_map: dict[str, tuple[type[Any], str, str | None]] = {
        "knowledge_entity": (KnowledgeEntity, "name", "entity_type"),
        "memory_record": (MemoryRecord, "title", "memory_type"),
        "brand_document": (BrandDocument, "title", "document_type"),
        "idea": (Idea, "title", "status"),
        "content_item": (ContentItem, "title", "status"),
        "content_brief": (ContentBrief, "title", "platform"),
        "script": (Script, "title", "status"),
        "production_plan": (ProductionPlan, "title", "status"),
        "asset": (Asset, "filename", "media_type"),
        "proof_item": (ProofItem, "title", "proof_type"),
        "creator": (Creator, "name", "platform"),
        "benchmark_content": (BenchmarkContent, "title", "platform"),
        "experiment": (Experiment, "title", "platform"),
    }
    if normalized == "metric_snapshot":
        metric = db.get(MetricSnapshot, node_id)
        if metric:
            return GraphRelatedNode(
                node_type=normalized,
                node_id=node_id,
                title=f"{metric.platform} metric snapshot",
                subtitle=f"{metric.views} views, {metric.engagement} engagements",
                href="/analytics",
            )
    entry = model_map.get(normalized)
    if not entry:
        return GraphRelatedNode(node_type=normalized, node_id=node_id, title=node_id)
    model, title_field, subtitle_field = entry
    item = db.get(model, node_id)
    if not item:
        return GraphRelatedNode(node_type=normalized, node_id=node_id, title=node_id)
    title = str(getattr(item, title_field))
    subtitle_value = getattr(item, subtitle_field) if subtitle_field else None
    subtitle = getattr(subtitle_value, "value", subtitle_value)
    href_map = {
        "knowledge_entity": "/memory",
        "memory_record": "/memory",
        "brand_document": "/brand",
        "idea": "/ideas",
        "content_item": "/pipeline",
        "content_brief": "/studio",
        "script": "/studio",
        "production_plan": "/production",
        "asset": "/assets",
        "proof_item": "/proof",
        "creator": "/benchmarks",
        "benchmark_content": "/benchmarks",
        "experiment": "/analytics",
    }
    return GraphRelatedNode(
        node_type=normalized,
        node_id=node_id,
        title=title,
        subtitle=str(subtitle) if subtitle is not None else None,
        href=href_map.get(normalized),
    )


def graph_neighborhood(
    db: Session,
    node_type: str,
    node_id: str,
    limit: int,
) -> MemoryGraphNeighborhood:
    brand = _active_brand(db)
    normalized = _node_type(node_type)
    edges = list(
        db.scalars(
            select(KnowledgeEdge)
            .where(
                KnowledgeEdge.brand_id == brand.id,
                KnowledgeEdge.sensitivity != "restricted",
                or_(
                    (KnowledgeEdge.source_type == normalized)
                    & (KnowledgeEdge.source_id == node_id),
                    (KnowledgeEdge.target_type == normalized)
                    & (KnowledgeEdge.target_id == node_id),
                ),
            )
            .order_by(KnowledgeEdge.confidence.desc(), KnowledgeEdge.updated_at.desc())
            .limit(limit)
        ).all()
    )
    related: list[GraphRelatedNode] = []
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        if edge.source_type == normalized and edge.source_id == node_id:
            related_type = edge.target_type
            related_id = edge.target_id
        else:
            related_type = edge.source_type
            related_id = edge.source_id
        key = (related_type, related_id)
        if key in seen:
            continue
        seen.add(key)
        related.append(_describe_node(db, related_type, related_id))
    return MemoryGraphNeighborhood(
        node_type=normalized,
        node_id=node_id,
        edges=edges,
        related_nodes=related,
    )


def graph_search(db: Session, query: str, limit: int) -> list[MemoryGraphSearchResult]:
    brand = _active_brand(db)
    pattern = f"%{query}%"
    results: list[MemoryGraphSearchResult] = []
    entities = db.scalars(
        select(KnowledgeEntity)
        .where(
            KnowledgeEntity.brand_id == brand.id,
            KnowledgeEntity.sensitivity != "restricted",
            or_(
                KnowledgeEntity.name.ilike(pattern),
                KnowledgeEntity.description.ilike(pattern),
                KnowledgeEntity.slug.ilike(pattern),
            ),
        )
        .limit(limit)
    )
    for entity in entities:
        score = 8 if entity.name.lower() == query.lower() else 3
        if query.lower() in entity.name.lower():
            score += 4
        results.append(
            MemoryGraphSearchResult(
                id=entity.id,
                record_type=f"entity:{entity.entity_type}",
                title=entity.name,
                excerpt=entity.description[:240] or f"{entity.entity_type} entity",
                authority=entity.canonical_status.value,
                score=float(score + entity.confidence),
                confidence=entity.confidence,
                is_demo=entity.is_demo,
            )
        )

    edges = db.scalars(
        select(KnowledgeEdge)
        .where(
            KnowledgeEdge.brand_id == brand.id,
            KnowledgeEdge.sensitivity != "restricted",
            or_(
                KnowledgeEdge.relationship_type.ilike(pattern),
                KnowledgeEdge.label.ilike(pattern),
            ),
        )
        .limit(limit)
    )
    for edge in edges:
        score = 2 + edge.confidence
        results.append(
            MemoryGraphSearchResult(
                id=edge.id,
                record_type=f"edge:{edge.relationship_type}",
                title=edge.label,
                excerpt=(
                    f"{edge.source_type}:{edge.source_id} -> "
                    f"{edge.target_type}:{edge.target_id}"
                ),
                authority=edge.canonical_status.value,
                score=float(score),
                confidence=edge.confidence,
                is_demo=edge.is_demo,
            )
        )

    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def graph_conflicts(db: Session, limit: int) -> list[KnowledgeEdge]:
    brand = _active_brand(db)
    return list(
        db.scalars(
            select(KnowledgeEdge)
            .where(
                KnowledgeEdge.brand_id == brand.id,
                KnowledgeEdge.relationship_type == "contradicts",
            )
            .order_by(KnowledgeEdge.updated_at.desc())
            .limit(limit)
        ).all()
    )


def graph_pending_approvals(db: Session, limit: int) -> list[KnowledgeEdge]:
    brand = _active_brand(db)
    return list(
        db.scalars(
            select(KnowledgeEdge)
            .where(
                KnowledgeEdge.brand_id == brand.id,
                KnowledgeEdge.canonical_status == CanonicalStatus.WORKING,
                KnowledgeEdge.approved_at.is_(None),
            )
            .order_by(KnowledgeEdge.updated_at.desc())
            .limit(limit)
        ).all()
    )
