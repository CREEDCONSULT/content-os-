from __future__ import annotations

import re
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SkillDefinition

ROUTES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("brand strategy", "positioning", "brand boundary"), "01_brand_strategy"),
    (("audience", "persona"), "02_audience_intelligence"),
    (("creator", "benchmark", "teardown"), "03_creator_intelligence"),
    (("trend", "research"), "04_trend_research"),
    (("heartbeat", "daily intelligence", "daily brief"), "05_daily_heartbeat"),
    (("idea", "ideation"), "06_content_ideation"),
    (("brief",), "07_content_brief"),
    (("script",), "08_scriptwriting"),
    (("hook",), "09_hook_lab"),
    (("founder story", "storytelling"), "10_founder_storytelling"),
    (("platform", "adapt"), "11_platform_adaptation"),
    (("creative direction", "visual concept"), "12_creative_direction"),
    (("production", "shot", "scene"), "13_production_planning"),
    (("visual review", "thumbnail"), "14_visual_review"),
    (("caption", "copy"), "15_caption_copy"),
    (("financial", "investment", "etf", "crypto"), "16_financial_content_safety"),
    (("fact check", "verify", "citation"), "17_fact_checking"),
    (("pipeline", "status", "workflow"), "18_content_pipeline"),
    (("calendar", "schedule", "capacity"), "19_calendar_orchestration"),
    (("analytics", "metric", "performance"), "20_analytics_review"),
    (("experiment", "hypothesis", "test"), "21_experimentation"),
    (("proof", "case study", "evidence"), "22_proof_of_work"),
    (("asset", "media library"), "23_asset_management"),
    (("telegram", "voice note"), "24_telegram_capture"),
    (("memory", "vault", "retrieve"), "25_brand_memory"),
    (("context", "context pack"), "26_context_pack_builder"),
    (("transparency", "agent run", "audit"), "27_agent_transparency"),
    (("publish", "public", "outreach"), "28_publishing_safety"),
)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def route_skill_slugs(intent: str, raw_input: dict[str, object]) -> list[str]:
    haystack = _normalise(f"{intent} {raw_input}")
    selected = ["00_skill_router"]
    for keywords, slug in ROUTES:
        if any(keyword in haystack for keyword in keywords):
            selected.append(slug)
    if len(selected) == 1:
        selected.append("29_general_brand_assistant")
    selected.extend(["26_context_pack_builder", "27_agent_transparency"])
    return list(dict.fromkeys(selected))


def load_skills(db: Session, slugs: Iterable[str]) -> list[SkillDefinition]:
    requested = list(dict.fromkeys(slugs))
    if not requested:
        return []
    records = list(
        db.scalars(
            select(SkillDefinition).where(
                SkillDefinition.slug.in_(requested),
                SkillDefinition.enabled.is_(True),
            )
        ).all()
    )
    order = {slug: index for index, slug in enumerate(requested)}
    return sorted(records, key=lambda item: order.get(item.slug, len(order)))
