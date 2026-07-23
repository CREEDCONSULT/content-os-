from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path, PurePosixPath

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import (
    Brand,
    BrandDocument,
    BrandDocumentVersion,
    CanonicalStatus,
    DailyBrief,
    Idea,
    MemoryRecord,
    Script,
    ScriptStatus,
    ScriptVersion,
    SyncEvent,
)
from app.schemas.contracts import MemoryRecordCreate, MemorySearchResult, VaultSyncResult

VAULT_FOLDERS = (
    "00_Command_Center",
    "01_Brand_Core/Canonical Decisions",
    "02_Content_Strategy/Campaigns",
    "02_Content_Strategy/Monthly Themes",
    "03_Ideas/Inbox",
    "03_Ideas/Selected",
    "03_Ideas/Researching",
    "03_Ideas/Archived",
    "03_Ideas/Voice Notes",
    "04_Benchmarks/Creators",
    "04_Benchmarks/Content References",
    "04_Benchmarks/Hook Library",
    "04_Benchmarks/Story Patterns",
    "04_Benchmarks/Visual Patterns",
    "04_Benchmarks/Editing Patterns",
    "04_Benchmarks/Language Patterns",
    "04_Benchmarks/Trend Watch",
    "05_Research/Daily Intelligence",
    "05_Research/Weekly Intelligence",
    "05_Research/Monthly Reviews",
    "05_Research/Topic Research",
    "05_Research/Market Research",
    "05_Research/Platform Research",
    "05_Research/Source Notes",
    "06_Content_Development/Briefs",
    "06_Content_Development/Scripts",
    "06_Content_Development/Carousels",
    "06_Content_Development/LinkedIn",
    "06_Content_Development/X",
    "06_Content_Development/YouTube",
    "06_Content_Development/Instagram",
    "06_Content_Development/TikTok",
    "06_Content_Development/Newsletter",
    "07_Production/Shoot Plans",
    "07_Production/Shot Lists",
    "07_Production/Lighting",
    "07_Production/Wardrobe",
    "07_Production/Locations",
    "07_Production/Editing Notes",
    "07_Production/Checklists",
    "08_Published_Content/2026/August",
    "08_Published_Content/2026/September",
    "08_Published_Content/2026/October",
    "08_Published_Content/2026/November",
    "08_Published_Content/2026/December",
    "09_Analytics/Platform Snapshots",
    "09_Analytics/Content Reviews",
    "09_Analytics/Hook Performance",
    "09_Analytics/Series Performance",
    "09_Analytics/Audience Signals",
    "09_Analytics/Experiments",
    "09_Analytics/Lessons",
    "10_Proof_of_Work/Case Studies",
    "10_Proof_of_Work/Testimonials",
    "10_Proof_of_Work/Project Evidence",
    "10_Proof_of_Work/Speaking",
    "10_Proof_of_Work/Media",
    "11_Founder_Stories/Green Stories",
    "11_Founder_Stories/Yellow Stories",
    "11_Founder_Stories/Restricted Stories",
    "12_Agent_Memory/Working Memory",
    "12_Agent_Memory/Decisions",
    "12_Agent_Memory/Preferences",
    "12_Agent_Memory/Rejected Ideas",
    "12_Agent_Memory/Learned Patterns",
    "12_Agent_Memory/Model Evaluations",
    "12_Agent_Memory/Agent Run Summaries",
    "13_Templates",
    "99_Archive",
)


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def _checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts or path.suffix.lower() != ".md":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Vault path must be a safe relative Markdown path.",
        )
    return path.as_posix()


def _target(root: Path, relative: str) -> Path:
    target = (root / _safe_relative(relative)).resolve()
    if root != target and root not in target.parents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Vault path escapes the configured root.",
        )
    return target


def vault_root(settings: Settings) -> Path:
    root = Path(settings.brandos_vault_path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def initialize_vault(settings: Settings) -> tuple[Path, int]:
    root = vault_root(settings)
    created = 0
    for folder in VAULT_FOLDERS:
        path = root / folder
        if not path.exists():
            created += 1
        path.mkdir(parents=True, exist_ok=True)
    marker = root / ".brandos-vault"
    if not marker.exists():
        marker.write_text(
            "Mezie BrandOS vault\nOperational source of truth: PostgreSQL\n",
            encoding="utf-8",
        )
    return root, created


def _contains_configured_secret(content: str, settings: Settings) -> bool:
    values = [
        secret.get_secret_value()
        for secret in (
            settings.openai_api_key,
            settings.telegram_bot_token,
            settings.telegram_webhook_secret,
            settings.apify_token,
            settings.creedai_memory_api_key,
        )
        if secret and len(secret.get_secret_value()) >= 8
    ]
    return any(value in content for value in values)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _frontmatter(
    *,
    record_type: str,
    record_id: str,
    title: str,
    authority: str,
    body: str,
) -> str:
    safe_title = title.replace('"', "'")
    return "\n".join(
        [
            "---",
            f'brandos_record_type: "{record_type}"',
            f'brandos_record_id: "{record_id}"',
            f'authority: "{authority}"',
            f'title: "{safe_title}"',
            "---",
            "",
            f"# {title}",
            "",
            body.strip(),
            "",
        ]
    )


def _export_specs(
    db: Session,
    brand: Brand,
) -> list[tuple[str, str, str, str, str, CanonicalStatus, str, bool]]:
    specs: list[tuple[str, str, str, str, str, CanonicalStatus, str, bool]] = []
    documents = list(
        db.scalars(
            select(BrandDocument).where(
                BrandDocument.brand_id == brand.id,
                BrandDocument.canonical_status == CanonicalStatus.CANONICAL,
            )
        ).all()
    )
    for document in documents:
        version = db.get(BrandDocumentVersion, document.current_version_id)
        if not version:
            continue
        relative = f"01_Brand_Core/{document.slug}.md"
        rendered = _frontmatter(
            record_type="brand_document",
            record_id=document.id,
            title=document.title,
            authority="canonical",
            body=version.content_markdown,
        )
        specs.append(
            (
                "brand_document",
                document.id,
                document.title,
                relative,
                rendered,
                CanonicalStatus.CANONICAL,
                document.sensitivity,
                False,
            )
        )

    scripts = list(
        db.scalars(
            select(Script).where(
                Script.brand_id == brand.id,
                Script.status == ScriptStatus.APPROVED,
            )
        ).all()
    )
    for script in scripts:
        version = db.get(ScriptVersion, script.current_version_id)
        if not version:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", script.title.lower()).strip("-")[:120]
        relative = f"06_Content_Development/Scripts/{slug}-{script.id[:8]}.md"
        body = "\n\n".join(
            [
                f"**Hook:** {version.hook_selected}",
                version.body_text,
                f"**CTA:** {version.cta}",
                f"**Version:** {version.version_number}",
                f"**Checksum:** `{version.checksum_sha256}`",
            ]
        )
        rendered = _frontmatter(
            record_type="approved_script",
            record_id=script.id,
            title=script.title,
            authority="approved",
            body=body,
        )
        specs.append(
            (
                "approved_script",
                script.id,
                script.title,
                relative,
                rendered,
                CanonicalStatus.WORKING,
                "internal",
                script.is_demo,
            )
        )

    briefs = list(
        db.scalars(
            select(DailyBrief)
            .where(DailyBrief.brand_id == brand.id)
            .order_by(DailyBrief.brief_date)
        ).all()
    )
    for brief in briefs:
        relative = f"05_Research/Daily Intelligence/{brief.brief_date.isoformat()}.md"
        body = "\n\n".join(
            [
                "## What changed\n"
                + "\n".join(f"- {item.get('summary', item)}" for item in brief.what_changed),
                "## Creator watch\n"
                + "\n".join(f"- {item.get('summary', item)}" for item in brief.creator_watch),
                "## Content opportunities\n"
                + "\n".join(f"- {item.get('title', item)}" for item in brief.content_opportunities),
                "## Risks and noise\n" + "\n".join(f"- {item}" for item in brief.risks_noise),
                "## Recommended action\n" + brief.recommended_action,
                "## Coverage gaps\n" + "\n".join(f"- {item}" for item in brief.coverage_gaps),
            ]
        )
        rendered = _frontmatter(
            record_type="daily_brief",
            record_id=brief.id,
            title=brief.title,
            authority="working",
            body=body,
        )
        specs.append(
            (
                "daily_brief",
                brief.id,
                brief.title,
                relative,
                rendered,
                CanonicalStatus.WORKING,
                "internal",
                brief.is_demo,
            )
        )
    return specs


def _event(
    db: Session,
    brand_id: str,
    *,
    direction: str,
    record_type: str,
    record_id: str | None,
    vault_path: str,
    status_value: str,
    database_checksum: str | None,
    vault_checksum: str | None,
    details: dict[str, object] | None = None,
) -> SyncEvent:
    event = SyncEvent(
        brand_id=brand_id,
        direction=direction,
        record_type=record_type,
        record_id=record_id,
        vault_path=vault_path,
        status=status_value,
        database_checksum=database_checksum,
        vault_checksum=vault_checksum,
        details=details or {},
    )
    db.add(event)
    db.flush()
    return event


def sync_vault(db: Session, settings: Settings) -> VaultSyncResult:
    brand = _active_brand(db)
    root, initialized = initialize_vault(settings)
    exported = imported = conflicts = skipped = 0
    events: list[SyncEvent] = []

    for (
        record_type,
        record_id,
        title,
        relative,
        rendered,
        authority,
        sensitivity,
        is_demo,
    ) in _export_specs(db, brand):
        if _contains_configured_secret(rendered, settings):
            events.append(
                _event(
                    db,
                    brand.id,
                    direction="database_to_vault",
                    record_type=record_type,
                    record_id=record_id,
                    vault_path=relative,
                    status_value="blocked_secret",
                    database_checksum=_checksum(rendered),
                    vault_checksum=None,
                )
            )
            skipped += 1
            continue
        target = _target(root, relative)
        database_checksum = _checksum(rendered)
        existing = db.scalar(
            select(MemoryRecord).where(
                MemoryRecord.brand_id == brand.id,
                MemoryRecord.vault_path == relative,
            )
        )
        vault_checksum = _checksum(target.read_text(encoding="utf-8")) if target.exists() else None
        if existing and vault_checksum and vault_checksum != existing.content_checksum:
            existing.sync_status = "conflict"
            events.append(
                _event(
                    db,
                    brand.id,
                    direction="reconcile",
                    record_type=record_type,
                    record_id=record_id,
                    vault_path=relative,
                    status_value="conflict",
                    database_checksum=database_checksum,
                    vault_checksum=vault_checksum,
                    details={
                        "reason": "Vault content changed after the last synchronized version.",
                        "resolution": "Preserved both copies; user review required.",
                    },
                )
            )
            conflicts += 1
            continue
        if not existing and target.exists():
            events.append(
                _event(
                    db,
                    brand.id,
                    direction="reconcile",
                    record_type=record_type,
                    record_id=record_id,
                    vault_path=relative,
                    status_value="conflict",
                    database_checksum=database_checksum,
                    vault_checksum=vault_checksum,
                    details={"reason": "An untracked vault file already occupies the export path."},
                )
            )
            conflicts += 1
            continue
        if vault_checksum == database_checksum:
            skipped += 1
            continue
        _atomic_write(target, rendered)
        if existing:
            existing.title = title
            existing.content = rendered
            existing.canonical_status = authority
            existing.content_checksum = database_checksum
            existing.sync_status = "synced"
            existing.provenance = {"record_type": record_type, "record_id": record_id}
        else:
            db.add(
                MemoryRecord(
                    brand_id=brand.id,
                    memory_type=record_type,
                    title=title,
                    content=rendered,
                    canonical_status=authority,
                    confidence=1,
                    provenance={"record_type": record_type, "record_id": record_id},
                    vault_path=relative,
                    content_checksum=database_checksum,
                    sensitivity=sensitivity,
                    sync_status="synced",
                    embedding_status=("pending" if settings.brand_embedding_model else "disabled"),
                    is_demo=is_demo,
                )
            )
        events.append(
            _event(
                db,
                brand.id,
                direction="database_to_vault",
                record_type=record_type,
                record_id=record_id,
                vault_path=relative,
                status_value="exported",
                database_checksum=database_checksum,
                vault_checksum=database_checksum,
            )
        )
        exported += 1

    for path in sorted(root.rglob("*.md")):
        if ".obsidian" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8")
        content_checksum = _checksum(content)
        existing = db.scalar(
            select(MemoryRecord).where(
                MemoryRecord.brand_id == brand.id,
                MemoryRecord.vault_path == relative,
            )
        )
        if existing:
            if existing.content_checksum == content_checksum:
                continue
            if existing.canonical_status == CanonicalStatus.CANONICAL:
                if existing.sync_status != "conflict":
                    existing.sync_status = "conflict"
                    conflicts += 1
                continue
            existing.content = content
            existing.content_checksum = content_checksum
            existing.sync_status = "imported"
            existing.provenance = {**existing.provenance, "last_import": relative}
            imported += 1
            events.append(
                _event(
                    db,
                    brand.id,
                    direction="vault_to_database",
                    record_type=existing.memory_type,
                    record_id=existing.id,
                    vault_path=relative,
                    status_value="imported",
                    database_checksum=content_checksum,
                    vault_checksum=content_checksum,
                )
            )
            continue
        title_match = re.search(r"(?m)^#\s+(.+)$", content)
        title = title_match.group(1).strip()[:240] if title_match else path.stem[:240]
        memory = MemoryRecord(
            brand_id=brand.id,
            memory_type="vault_note",
            title=title,
            content=content,
            canonical_status=CanonicalStatus.WORKING,
            confidence=0.5,
            provenance={"source": "vault_import", "path": relative},
            vault_path=relative,
            content_checksum=content_checksum,
            sensitivity="internal",
            sync_status="imported",
            embedding_status="pending" if settings.brand_embedding_model else "disabled",
        )
        db.add(memory)
        db.flush()
        if relative.startswith("03_Ideas/Inbox/"):
            existing_idea = db.scalar(
                select(Idea).where(Idea.source_reference == f"vault:{relative}")
            )
            if not existing_idea:
                db.add(
                    Idea(
                        brand_id=brand.id,
                        title=title,
                        raw_input=content[:20_000],
                        source_type="vault",
                        source_reference=f"vault:{relative}",
                        platform_fit=[],
                        is_demo=False,
                    )
                )
        imported += 1
        events.append(
            _event(
                db,
                brand.id,
                direction="vault_to_database",
                record_type="vault_note",
                record_id=memory.id,
                vault_path=relative,
                status_value="imported",
                database_checksum=content_checksum,
                vault_checksum=content_checksum,
            )
        )

    db.commit()
    return VaultSyncResult(
        root=str(root),
        initialized_folders=initialized,
        exported=exported,
        imported=imported,
        conflicts=conflicts,
        skipped=skipped,
        events=events,
    )


def create_memory_record(
    db: Session,
    settings: Settings,
    payload: MemoryRecordCreate,
) -> MemoryRecord:
    brand = _active_brand(db)
    relative = _safe_relative(payload.vault_path)
    if db.scalar(
        select(MemoryRecord.id).where(
            MemoryRecord.brand_id == brand.id,
            MemoryRecord.vault_path == relative,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A memory record already owns this vault path.",
        )
    if _contains_configured_secret(payload.content, settings):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Configured secret material cannot be written to the vault.",
        )
    root, _ = initialize_vault(settings)
    rendered = _frontmatter(
        record_type=payload.memory_type,
        record_id="pending",
        title=payload.title,
        authority="working",
        body=payload.content,
    )
    record = MemoryRecord(
        brand_id=brand.id,
        **payload.model_dump(exclude={"vault_path", "content"}),
        content=rendered,
        canonical_status=CanonicalStatus.WORKING,
        provenance={"source": "dashboard"},
        vault_path=relative,
        content_checksum=_checksum(rendered),
        sync_status="synced",
        embedding_status="pending" if settings.brand_embedding_model else "disabled",
    )
    db.add(record)
    db.flush()
    rendered = rendered.replace('brandos_record_id: "pending"', f'brandos_record_id: "{record.id}"')
    record.content = rendered
    record.content_checksum = _checksum(rendered)
    _atomic_write(_target(root, relative), rendered)
    db.commit()
    db.refresh(record)
    return record


def search_memory(
    db: Session,
    query: str,
    limit: int,
) -> list[MemorySearchResult]:
    brand = _active_brand(db)
    terms = {term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) >= 3}
    results: list[MemorySearchResult] = []
    records = list(
        db.scalars(
            select(MemoryRecord).where(
                MemoryRecord.brand_id == brand.id,
                MemoryRecord.sensitivity != "restricted",
            )
        ).all()
    )
    for record in records:
        corpus = f"{record.title} {record.content}".lower()
        matches = sum(corpus.count(term) for term in terms)
        if not matches:
            continue
        authority_bonus = 3 if record.canonical_status == CanonicalStatus.CANONICAL else 1
        score = matches + authority_bonus + record.confidence
        results.append(
            MemorySearchResult(
                id=record.id,
                record_type=record.memory_type,
                title=record.title,
                excerpt=record.content[:360],
                authority=record.canonical_status.value,
                source_path=record.vault_path,
                score=round(score, 2),
                confidence=record.confidence,
                is_demo=record.is_demo,
            )
        )
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
