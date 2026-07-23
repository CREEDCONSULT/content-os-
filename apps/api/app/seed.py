from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    AgentRun,
    ApprovalStatus,
    AuditEvent,
    Brand,
    BrandDocument,
    BrandDocumentVersion,
    CanonicalStatus,
    ContentItem,
    Idea,
    IdeaStatus,
    MetricSnapshot,
    PipelineStatus,
    Task,
)
from app.db.session import SessionLocal
from app.schemas.contracts import IdeaScores
from app.services.ideas import apply_scores

BRAND_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, "https://meziebrandos.local/brands/mr-c-mezie"))


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:220]


def document_type(path: Path) -> str:
    name = path.name.lower()
    if "skill" in name or path.parent.name[:2].isdigit():
        return "skill"
    if "positioning" in name:
        return "positioning"
    if "uiux" in name:
        return "visual-system"
    if "technical" in name:
        return "technical-architecture"
    if "product_requirements" in name:
        return "product-requirements"
    if "autonomous" in name:
        return "memory-heartbeat"
    if "execution" in str(path).lower():
        return "brand-execution"
    return "brand-record"


def title_from_markdown(path: Path, content: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()[:240]
    return path.stem.replace("_", " ")[:240]


def resolve_source_root() -> Path:
    settings = get_settings()
    candidates = []
    if settings.source_documents_path:
        candidates.append(Path(settings.source_documents_path))
    module_path = Path(__file__).resolve()
    if len(module_path.parents) > 3:
        candidates.append(module_path.parents[3] / "docs" / "source")
    candidates.append(Path("/app/source-documents"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("BrandOS source documents were not found.")


def seed_brand(db: Session) -> Brand:
    brand = db.get(Brand, BRAND_ID)
    if brand:
        return brand
    brand = Brand(
        id=BRAND_ID,
        name="Mr. C. Mezie",
        founder_name="Mesomachukwu Mezie-Akabudu",
        category="Builder Intelligence",
        positioning=(
            "Mr. C. Mezie helps ambitious builders turn ideas, technology, and opportunity "
            "into systems, businesses, and ownership."
        ),
        signature_line="See the possibility. Build the system. Become the evidence.",
    )
    db.add(brand)
    db.commit()
    return brand


def import_documents(db: Session, brand: Brand, source_root: Path) -> int:
    imported = 0
    for path in sorted(source_root.rglob("*.md")):
        relative = path.relative_to(source_root).as_posix()
        content = path.read_text(encoding="utf-8-sig")
        slug = slugify(relative.removesuffix(".md"))
        existing = db.scalar(
            select(BrandDocument).where(
                BrandDocument.brand_id == brand.id,
                BrandDocument.slug == slug,
            )
        )
        if existing:
            continue
        status = CanonicalStatus.CANONICAL
        document = BrandDocument(
            brand_id=brand.id,
            document_type=document_type(path),
            title=title_from_markdown(path, content),
            slug=slug,
            canonical_status=status,
            source_path=f"docs/source/{relative}",
            sensitivity="internal",
            tags=[document_type(path), "source-import", "2026"],
            version_count=1,
        )
        db.add(document)
        db.flush()
        version = BrandDocumentVersion(
            brand_document_id=document.id,
            version_number=1,
            content_markdown=content,
            change_summary="Initial source import",
            checksum_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            provenance={"source_path": document.source_path, "imported": True},
            created_by="system:source-import",
            is_active=True,
        )
        db.add(version)
        db.flush()
        document.current_version_id = version.id
        imported += 1
    db.commit()
    return imported


def seed_workspace(db: Session, brand: Brand) -> None:
    if db.scalar(select(Idea.id).where(Idea.brand_id == brand.id).limit(1)):
        return

    idea_specs = [
        (
            "AI is leverage, not identity",
            "Show a real workflow where AI extends judgment instead of replacing it.",
            "Leverage",
            "Built With AI",
            ["Instagram", "LinkedIn"],
            (9.6, 9.1, 9.2, 8.8, 8.7, 9.0, 9.5),
            IdeaStatus.SELECTED,
        ),
        (
            "The system behind a consistent founder",
            "A Builder Walk about replacing motivation with a weekly operating system.",
            "Lead",
            "Builder Walks",
            ["Instagram", "TikTok"],
            (9.4, 9.0, 8.1, 8.0, 8.4, 9.3, 8.9),
            IdeaStatus.RESEARCHING,
        ),
        (
            "Building BrandOS in public",
            "Document the architecture and the reason every idea needs provenance "
            "and a next action.",
            "Build",
            "Building Creed",
            ["LinkedIn", "YouTube"],
            (9.8, 8.9, 9.7, 9.3, 9.1, 8.2, 9.8),
            IdeaStatus.SELECTED,
        ),
        (
            "Ownership School: ETFs without the fog",
            "Explain the structure, diversification, fees, risks, and what to research "
            "next. No signals.",
            "Own",
            "Ownership School",
            ["Instagram", "YouTube"],
            (8.8, 9.2, 8.0, 7.5, 8.2, 8.6, 8.4),
            IdeaStatus.CAPTURED,
        ),
        (
            "Africa does not have a talent problem",
            "Explore bridges of trust, knowledge, capital, and systems without "
            "romanticizing the gap.",
            "See",
            "Africa Can Build",
            ["LinkedIn", "YouTube"],
            (9.3, 8.8, 7.7, 8.4, 8.9, 7.2, 9.0),
            IdeaStatus.CLARIFYING,
        ),
    ]
    ideas: list[Idea] = []
    for title, raw, pillar, series, platforms, values, idea_status in idea_specs:
        idea = Idea(
            brand_id=brand.id,
            title=title,
            raw_input=raw,
            source_type="seed",
            pillar=pillar,
            series=series,
            audience="Emerging Builder",
            platform_fit=platforms,
            strategic_objective="Build clear association with Builder Intelligence",
            urgency="normal",
            status=idea_status,
            is_demo=True,
        )
        scores = IdeaScores(
            brand_fit_score=values[0],
            audience_value_score=values[1],
            proof_score=values[2],
            timeliness_score=values[3],
            originality_score=values[4],
            feasibility_score=values[5],
            strategic_importance_score=values[6],
        )
        apply_scores(idea, scores)
        db.add(idea)
        db.flush()
        ideas.append(idea)

    today = datetime.now(UTC).date()
    content_specs = [
        (
            ideas[2],
            "Building my personal Brand OS",
            "LinkedIn",
            "Post",
            "Build",
            PipelineStatus.SCRIPT,
            1,
        ),
        (
            ideas[0],
            "AI is leverage, not identity",
            "Instagram",
            "Reel",
            "Leverage",
            PipelineStatus.REVIEW,
            2,
        ),
        (
            ideas[1],
            "The system behind consistency",
            "Instagram",
            "Builder Walk",
            "Lead",
            PipelineStatus.READY_TO_SHOOT,
            3,
        ),
        (ideas[3], "ETFs without the fog", "YouTube", "Short", "Own", PipelineStatus.RESEARCH, 5),
        (
            ideas[4],
            "Africa's people are the opportunity",
            "LinkedIn",
            "Essay",
            "See",
            PipelineStatus.BRIEF,
            8,
        ),
        (
            None,
            "Becoming the Evidence — August",
            "YouTube",
            "Founder Review",
            "Lead",
            PipelineStatus.EDITING,
            10,
        ),
        (
            None,
            "What a product dashboard should remember",
            "X",
            "Thread",
            "Create",
            PipelineStatus.PUBLISHED,
            -3,
        ),
    ]
    content_items: list[ContentItem] = []
    for idea, title, platform, format_name, pillar, pipeline_status, due_offset in content_specs:
        item = ContentItem(
            brand_id=brand.id,
            idea_id=idea.id if idea else None,
            title=title,
            platform=platform,
            format=format_name,
            pillar=pillar,
            series=idea.series if idea else "Becoming the Evidence",
            audience="Emerging Builder",
            objective="Build authority through useful, evidence-led content",
            status=pipeline_status,
            priority="high" if due_offset <= 3 else "medium",
            due_date=today + timedelta(days=due_offset),
            readiness_score={
                PipelineStatus.RESEARCH: 20,
                PipelineStatus.BRIEF: 35,
                PipelineStatus.SCRIPT: 50,
                PipelineStatus.REVIEW: 65,
                PipelineStatus.READY_TO_SHOOT: 85,
                PipelineStatus.EDITING: 75,
                PipelineStatus.PUBLISHED: 100,
            }[pipeline_status],
            approval_status=(
                ApprovalStatus.APPROVED
                if pipeline_status == PipelineStatus.PUBLISHED
                else ApprovalStatus.NOT_REQUIRED
            ),
            is_demo=True,
        )
        db.add(item)
        db.flush()
        content_items.append(item)

    task_specs = [
        ("Research current AI workflow examples", 9, "high"),
        ("Review BrandOS build-in-public script", 11, "high"),
        ("Record Builder Walk test take", 14, "medium"),
        ("Verify ETF explainer sources", 16, "high"),
        ("Complete daily BrandOS review", 18, "low"),
    ]
    now = datetime.now(UTC)
    for title, hour, priority in task_specs:
        due = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if due < now:
            due += timedelta(days=1)
        db.add(
            Task(
                brand_id=brand.id,
                title=title,
                due_at=due,
                priority=priority,
                is_demo=True,
            )
        )

    db.add(
        MetricSnapshot(
            brand_id=brand.id,
            content_item_id=content_items[-1].id,
            platform="X",
            views=18_300,
            impressions=24_100,
            engagement=1_126,
            saves=83,
            shares=47,
            is_demo=True,
        )
    )
    db.add(
        AgentRun(
            brand_id=brand.id,
            channel="seed",
            intent="Prepare the first BrandOS workspace",
            status="completed",
            model_alias="mock_brand_fast_model",
            skills_used=["00_skill_router", "27_agent_transparency"],
            tools_used=["database"],
            context_loaded=[],
            confidence=1.0,
            summary="Deterministic demo workspace seeded. No external model was called.",
            is_demo=True,
        )
    )
    for idea in ideas[:3]:
        db.add(
            AuditEvent(
                brand_id=brand.id,
                event_type="idea.seeded",
                actor="system:seed",
                target_type="idea",
                target_id=idea.id,
                summary=f'Demo idea prepared: "{idea.title}"',
                is_demo=True,
            )
        )
    db.commit()


def seed_database(db: Session, source_root: Path | None = None) -> dict[str, int]:
    brand = seed_brand(db)
    imported = import_documents(db, brand, source_root or resolve_source_root())
    seed_workspace(db, brand)
    return {"documents_imported": imported}


def main() -> None:
    with SessionLocal() as db:
        result = seed_database(db)
    print(f"Seed complete: {result['documents_imported']} source documents imported.")


if __name__ == "__main__":
    main()
