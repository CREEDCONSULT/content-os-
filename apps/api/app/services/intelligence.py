from __future__ import annotations

import re
from datetime import UTC, date, datetime
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import (
    BenchmarkContent,
    Brand,
    Creator,
    DailyBrief,
    HeartbeatRun,
    HeartbeatSetting,
    MetricSnapshot,
)
from app.schemas.contracts import (
    BenchmarkCreate,
    CreatorCreate,
    HeartbeatSettingUpdate,
)
from app.services.context import build_context_pack
from app.services.memory import sync_vault


def active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def create_creator(db: Session, payload: CreatorCreate) -> Creator:
    brand = active_brand(db)
    existing = db.scalar(
        select(Creator).where(
            Creator.brand_id == brand.id,
            Creator.platform == payload.platform,
            Creator.username == payload.username,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This creator is already on the watchlist.",
        )
    creator = Creator(
        brand_id=brand.id,
        **payload.model_dump(),
        watch_status="active",
        is_demo=False,
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    platform_hosts = {
        "youtube": ("youtube.com", "youtu.be"),
        "instagram": ("instagram.com",),
        "tiktok": ("tiktok.com",),
        "linkedin": ("linkedin.com",),
        "x": ("x.com", "twitter.com"),
    }
    for platform, hosts in platform_hosts.items():
        if any(host.endswith(item) for item in hosts):
            return platform
    return "web"


def _phrase_set(value: str, width: int = 8) -> set[str]:
    words = re.findall(r"[a-z0-9']+", value.lower())
    return {" ".join(words[index : index + width]) for index in range(len(words) - width + 1)}


def create_benchmark(
    db: Session,
    payload: BenchmarkCreate,
    settings: Settings,
) -> BenchmarkContent:
    brand = active_brand(db)
    existing = db.scalar(
        select(BenchmarkContent).where(
            BenchmarkContent.brand_id == brand.id,
            BenchmarkContent.source_url == payload.source_url,
        )
    )
    if existing:
        return existing
    creator = db.get(Creator, payload.creator_id) if payload.creator_id else None
    if payload.creator_id and (not creator or creator.brand_id != brand.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found.",
        )
    platform = detect_platform(payload.source_url)
    limitations = [
        "Analysis is limited to operator-supplied metadata and excerpts.",
        "Audience response and performance were not independently verified.",
    ]
    evidence_level = "operator_excerpt" if payload.transcript_excerpt else "metadata_only"
    if not settings.apify_enabled:
        limitations.append("Apify is disabled; no external acquisition was attempted.")
    protected_identity = [
        "Do not reuse the creator's exact wording or signature phrases.",
        "Do not imitate creator-specific identity, persona, or distinctive visual branding.",
        "Do not imply the creator endorsed or collaborated on a Mezie adaptation.",
    ]
    adaptations = [
        (
            f"Apply the mechanic “{mechanic[:180]}” to an original Mr. C. Mezie "
            "Builder Intelligence idea using first-party proof and distinct language."
        )
        for mechanic in payload.transferable_mechanics[:5]
    ]
    source_phrases = _phrase_set(
        " ".join(
            filter(
                None,
                [
                    payload.transcript_excerpt,
                    payload.observed_hook,
                    payload.observed_structure,
                ],
            )
        )
    )
    if source_phrases and any(
        source_phrases.intersection(_phrase_set(adaptation)) for adaptation in adaptations
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Adaptation failed the eight-word copying safeguard.",
        )
    benchmark = BenchmarkContent(
        brand_id=brand.id,
        creator_id=creator.id if creator else None,
        source_url=payload.source_url,
        platform=platform,
        title=payload.title,
        source_type="manual_url",
        raw_metadata={
            "acquisition": "operator_supplied",
            "apify_attempted": False,
            "provider_state": "configured" if settings.apify_enabled else "disabled",
        },
        transcript_excerpt=payload.transcript_excerpt,
        hook_analysis=payload.observed_hook,
        structure_analysis=payload.observed_structure,
        visual_analysis=payload.visual_notes,
        editing_analysis=payload.editing_notes,
        transferable_mechanics=list(dict.fromkeys(payload.transferable_mechanics)),
        protected_identity=protected_identity,
        mezie_adaptations=adaptations,
        pattern_tags=list(dict.fromkeys(payload.pattern_tags)),
        limitations=limitations,
        evidence_level=evidence_level,
        status="analyzed",
        is_demo=False,
    )
    db.add(benchmark)
    if creator:
        creator.last_reviewed_at = datetime.now(UTC)
    db.commit()
    db.refresh(benchmark)
    return benchmark


def get_or_create_heartbeat_setting(db: Session) -> HeartbeatSetting:
    brand = active_brand(db)
    setting = db.scalar(select(HeartbeatSetting).where(HeartbeatSetting.brand_id == brand.id))
    if setting:
        return setting
    setting = HeartbeatSetting(
        brand_id=brand.id,
        enabled=False,
        schedule_hour=7,
        timezone="America/Toronto",
        mode="lean",
        max_sources=10,
        max_creators=5,
        telegram_summary_enabled=False,
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def update_heartbeat_setting(
    db: Session,
    payload: HeartbeatSettingUpdate,
) -> HeartbeatSetting:
    setting = get_or_create_heartbeat_setting(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    db.commit()
    db.refresh(setting)
    return setting


def _brief_for_run(db: Session, run: HeartbeatRun) -> DailyBrief | None:
    return db.scalar(select(DailyBrief).where(DailyBrief.heartbeat_run_id == run.id))


def run_heartbeat(
    db: Session,
    settings: Settings,
    *,
    run_date: date,
    trigger: str,
    idempotency_key: str,
) -> tuple[HeartbeatRun, DailyBrief, bool]:
    brand = active_brand(db)
    existing = db.scalar(
        select(HeartbeatRun).where(
            (HeartbeatRun.idempotency_key == idempotency_key)
            | ((HeartbeatRun.brand_id == brand.id) & (HeartbeatRun.run_date == run_date))
        )
    )
    if existing:
        brief = _brief_for_run(db, existing)
        if not brief:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Existing heartbeat run has no durable brief.",
            )
        return existing, brief, True

    setting = get_or_create_heartbeat_setting(db)
    pack = build_context_pack(
        db,
        brand.id,
        "Run the daily Brand Intelligence heartbeat",
        {"run_date": run_date.isoformat(), "mode": setting.mode},
    )
    creators = list(
        db.scalars(
            select(Creator)
            .where(
                Creator.brand_id == brand.id,
                Creator.watch_status == "active",
            )
            .order_by(Creator.tier, Creator.relevance_score.desc())
            .limit(setting.max_creators)
        ).all()
    )
    benchmarks = list(
        db.scalars(
            select(BenchmarkContent)
            .where(BenchmarkContent.brand_id == brand.id)
            .order_by(BenchmarkContent.updated_at.desc())
            .limit(setting.max_sources)
        ).all()
    )
    recent_metrics = list(
        db.scalars(
            select(MetricSnapshot)
            .where(MetricSnapshot.brand_id == brand.id)
            .order_by(MetricSnapshot.captured_at.desc())
            .limit(10)
        ).all()
    )
    coverage = [
        {
            "source": "brand_context",
            "status": pack.status,
            "records": len(pack.source_records),
        },
        {"source": "creator_watchlist", "status": "local", "records": len(creators)},
        {"source": "benchmark_library", "status": "local", "records": len(benchmarks)},
        {"source": "analytics", "status": "local", "records": len(recent_metrics)},
        {
            "source": "external_research",
            "status": "disabled" if not settings.apify_enabled else "not_run",
            "records": 0,
        },
    ]
    gaps: list[str] = []
    if not settings.apify_enabled:
        gaps.append(
            "External creator and trend acquisition is disabled; no freshness claim is made."
        )
    if not creators:
        gaps.append("The active creator watchlist is empty.")
    if not recent_metrics:
        gaps.append("No recent performance metrics are available.")

    creator_watch = [
        {
            "creator_id": creator.id,
            "name": creator.name,
            "tier": creator.tier,
            "summary": (
                f"{creator.name} remains a Tier {creator.tier} reference; "
                "no external activity check was performed."
            ),
            "classification": "approved_watchlist",
        }
        for creator in creators
    ]
    trends = [
        {
            "topic": tag,
            "platform": benchmark.platform,
            "velocity": "unknown",
            "relevance": 7,
            "evidence": benchmark.id,
            "brand_fit": 7,
            "risk": "Requires fresh source verification",
            "shelf_life": "unknown",
            "classification": "working_hypothesis",
        }
        for benchmark in benchmarks[:3]
        for tag in benchmark.pattern_tags[:1]
    ]
    mechanics = [
        mechanic for benchmark in benchmarks for mechanic in benchmark.transferable_mechanics
    ][:5]
    opportunities = [
        {
            "title": f"Build the Mezie evidence version of: {mechanic[:100]}",
            "hook": "The transferable lesson is not the creator's wording. It is the mechanism.",
            "pillar": ["Build", "Leverage", "Lead"][index % 3],
            "series": ["Building Creed", "Built With AI", "Builder Walks"][index % 3],
            "audience": "Emerging Builder",
            "platform": "LinkedIn",
            "why_now": "A stored benchmark exposes a reusable mechanism.",
            "supporting_evidence": [benchmark.id for benchmark in benchmarks[:2]],
            "mezie_angle": "Use first-party system-building evidence and original language.",
            "urgency": "research",
            "classification": "working_hypothesis",
        }
        for index, mechanic in enumerate(mechanics[:5])
    ]
    if not opportunities:
        opportunities = [
            {
                "title": "What BrandOS learned from making readiness explicit",
                "hook": (
                    "A plan is not ready because it exists. It is ready when blockers are gone."
                ),
                "pillar": "Build",
                "series": "Building Creed",
                "audience": "Emerging Builder",
                "platform": "LinkedIn",
                "why_now": "The local system contains verified implementation evidence.",
                "supporting_evidence": ["local:production-readiness"],
                "mezie_angle": "Show the operating rule and the proof boundary.",
                "urgency": "watch",
                "classification": "model_inference",
            }
        ]
    recommended = (
        "Review the first opportunity, attach a current source if it depends on external "
        "freshness, and convert only the strongest aligned item into an idea."
    )
    errors = list(gaps)
    run = HeartbeatRun(
        brand_id=brand.id,
        run_date=run_date,
        trigger=trigger,
        idempotency_key=idempotency_key,
        status="partial" if gaps else "completed",
        source_coverage=coverage,
        model_alias="deterministic_heartbeat_v1",
        tools_used=["database", "context_pack", "vault"],
        model_cost=0,
        tool_cost=0,
        context_pack_id=pack.id,
        records_changed=[],
        errors=errors,
        confidence=0.72 if gaps else 0.9,
        completed_at=datetime.now(UTC),
        is_demo=False,
    )
    db.add(run)
    db.flush()
    brief = DailyBrief(
        brand_id=brand.id,
        heartbeat_run_id=run.id,
        brief_date=run_date,
        title=f"Daily Brand Intelligence · {run_date.isoformat()}",
        what_changed=[
            {
                "summary": (
                    "Local BrandOS records were reviewed; external freshness sources "
                    "were not called."
                ),
                "classification": "verified_fact",
            }
        ],
        creator_watch=creator_watch,
        trend_signals=trends,
        content_opportunities=opportunities,
        risks_noise=[
            "Do not treat metadata-only benchmark patterns as performance proof.",
            "Do not copy creator wording, identity, or distinctive protected expression.",
        ],
        recommended_actions=[
            "Review the priority opportunity",
            "Add current evidence before making a freshness claim",
            "Keep public scheduling and publishing approval-gated",
        ],
        recommended_action=recommended,
        coverage_gaps=gaps,
        is_demo=False,
    )
    db.add(brief)
    db.flush()
    run.records_changed = [
        {"record_type": "daily_brief", "record_id": brief.id, "action": "created"}
    ]
    db.commit()
    sync_vault(db, settings)
    db.refresh(run)
    db.refresh(brief)
    memory = db.scalar(select(func.max(DailyBrief.vault_path)).where(DailyBrief.id == brief.id))
    if memory:
        brief.vault_path = str(memory)
    else:
        brief.vault_path = f"05_Research/Daily Intelligence/{brief.brief_date.isoformat()}.md"
    db.commit()
    db.refresh(brief)
    return run, brief, False
