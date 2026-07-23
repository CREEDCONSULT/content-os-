from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    AgentRun,
    ApprovalStatus,
    Asset,
    AuditEvent,
    BenchmarkContent,
    Brand,
    BrandDocument,
    BrandDocumentVersion,
    BriefStatus,
    CalendarEvent,
    CanonicalStatus,
    CapacityPlan,
    ContentBrief,
    ContentItem,
    Creator,
    DailyBrief,
    Experiment,
    HeartbeatRun,
    HeartbeatSetting,
    HookOption,
    Idea,
    IdeaStatus,
    Insight,
    MetricSnapshot,
    PipelineStatus,
    ProductionChecklistItem,
    ProductionPlan,
    ProductionScene,
    ProductionShot,
    ProductionStatus,
    ProofItem,
    ProofStatus,
    ReviewStatus,
    RightsStatus,
    Script,
    ScriptStatus,
    ScriptVersion,
    SkillDefinition,
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


def _markdown_section(content: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        content,
    )
    return match.group(1).strip() if match else ""


def _list_items(section: str) -> list[str]:
    items: list[str] = []
    for line in section.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line).strip()
        if cleaned and cleaned != line.strip():
            items.append(cleaned)
    return items


def import_skill_definitions(db: Session, source_root: Path) -> int:
    library_root = source_root / "skills" / "Mezie_BrandOS_Skill_Library_v1"
    if not library_root.exists():
        return 0
    imported = 0
    for path in sorted(library_root.glob("[0-9][0-9]_*/SKILL.md")):
        slug = path.parent.name
        if db.scalar(select(SkillDefinition.id).where(SkillDefinition.slug == slug)):
            continue
        content = path.read_text(encoding="utf-8-sig")
        title = title_from_markdown(path, content)
        purpose = _markdown_section(content, "Purpose")
        triggers = _markdown_section(content, "Triggers")
        required_context = _list_items(_markdown_section(content, "Required Context"))
        allowed_tools = _list_items(_markdown_section(content, "Tools and Dependencies"))
        workflow = _list_items(_markdown_section(content, "Workflow"))
        approval_policy = (
            _markdown_section(content, "Approval Rules") or "No approval rule supplied."
        )
        memory_policy = _markdown_section(content, "Memory Rules") or "No memory write."
        failure_behavior = (
            _markdown_section(content, "Failure Handling") or "Return a typed failed result."
        )
        high_reasoning = {
            "01_brand_strategy",
            "03_creator_intelligence",
            "04_trend_research",
            "16_financial_content_safety",
            "17_fact_checking",
            "20_analytics_review",
        }
        skill = SkillDefinition(
            slug=slug,
            name=title,
            version="1.0.0",
            description=purpose or title,
            trigger_summary=triggers or "Routed explicitly by the BrandOS Skill Router.",
            input_schema={
                "type": "object",
                "required": [
                    "request_id",
                    "user_id",
                    "brand_id",
                    "channel",
                    "intent",
                    "raw_input",
                    "permissions",
                    "budget",
                    "approval_state",
                ],
            },
            required_context=required_context,
            allowed_tools=allowed_tools,
            workflow=workflow,
            output_schema={
                "type": "object",
                "required": [
                    "skill",
                    "status",
                    "summary",
                    "outputs",
                    "sources",
                    "memory_writes",
                    "approvals_required",
                    "next_actions",
                    "confidence",
                ],
            },
            memory_policy=memory_policy,
            approval_policy=approval_policy,
            failure_behavior=failure_behavior,
            model_profile=("brand_quality_model" if slug in high_reasoning else "brand_fast_model"),
            timeout_seconds=180 if slug in high_reasoning else 120,
            cost_class="medium" if slug in high_reasoning else "low",
            source_path=f"docs/source/{path.relative_to(source_root).as_posix()}",
            checksum_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        db.add(skill)
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


def seed_authoring(db: Session, brand: Brand) -> int:
    if db.scalar(select(ContentBrief.id).where(ContentBrief.brand_id == brand.id).limit(1)):
        return 0
    idea = db.scalar(
        select(Idea).where(
            Idea.brand_id == brand.id,
            Idea.title == "Building BrandOS in public",
        )
    )
    if not idea:
        return 0
    content = db.scalar(select(ContentItem).where(ContentItem.idea_id == idea.id))
    if not content:
        return 0
    brief = ContentBrief(
        brand_id=brand.id,
        idea_id=idea.id,
        content_item_id=content.id,
        title="Building my personal Brand OS",
        objective="Show how a founder turns brand strategy into a governed operating system.",
        audience=idea.audience,
        platform="LinkedIn",
        format="Post",
        pillar="Build",
        series="Building Creed",
        core_message=idea.raw_input,
        audience_problem=(
            "Consistency fails when ideas, evidence, production, and learning are split."
        ),
        desired_emotion="clarity and constructive ambition",
        desired_action="Audit one disconnected part of your own creative workflow.",
        proof_points=[],
        benchmark_references=[],
        visual_direction="Editorial founder note with dark-and-gold system diagrams.",
        production_constraints=[
            "Use only verified product behavior.",
            "Do not imply public launch.",
        ],
        duration_seconds=90,
        cta="What part of your creative workflow needs a system?",
        success_metric="Qualified saves and builder replies",
        evidence_status=ReviewStatus.NEEDS_REVIEW,
        status=BriefStatus.READY,
        is_demo=True,
    )
    db.add(brief)
    db.flush()
    script = Script(
        brand_id=brand.id,
        content_brief_id=brief.id,
        content_item_id=content.id,
        title=brief.title,
        status=ScriptStatus.DRAFT,
        fact_check_status=ReviewStatus.NEEDS_REVIEW,
        version_count=1,
        is_demo=True,
    )
    db.add(script)
    db.flush()
    hook = "Consistency is not a personality trait. It is a system design problem."
    body = (
        "I used to think a stronger content habit was the answer. The real problem was that "
        "my ideas, brand rules, drafts, production, and learning lived in different places. "
        "So I started building BrandOS: one governed path from possibility to evidence. "
        "The lesson is simple: when the work matters, do not rely on memory and motivation. "
        "Build the system that makes the next right action visible."
    )
    version = ScriptVersion(
        script_id=script.id,
        version_number=1,
        body_text=body,
        hook_selected=hook,
        on_screen_text=["Possibility", "System", "Evidence"],
        b_roll_notes=["BrandOS command center", "Idea capture", "Approval queue"],
        camera_notes=["Direct-to-camera opening", "Screen recording for proof"],
        cta=brief.cta,
        duration_seconds=75,
        brand_alignment_score=9.3,
        originality_score=8.8,
        evidence_notes=["Demo draft; product claims require live verification before approval."],
        change_summary="Seeded first script draft",
        checksum_sha256=hashlib.sha256(f"{hook}\n{body}\n{brief.cta}".encode()).hexdigest(),
        created_by="system:seed",
        is_active=True,
    )
    db.add(version)
    db.flush()
    script.current_version_id = version.id
    hook_specs = [
        (hook, "declaration", 9.2, True),
        ("What if your content problem is really a systems problem?", "question", 8.8, False),
        ("I stopped chasing consistency and started engineering it.", "contrarian", 8.9, False),
    ]
    for text, category, score, recommended in hook_specs:
        db.add(
            HookOption(
                script_version_id=version.id,
                text=text,
                category=category,
                clarity_score=score,
                curiosity_score=score,
                specificity_score=score - 0.4,
                brand_fit_score=9.4,
                audience_fit_score=9.0,
                originality_score=8.8,
                total_score=score,
                is_recommended=recommended,
            )
        )
    db.commit()
    return 1


def seed_planning_and_proof(db: Session, brand: Brand) -> int:
    if db.scalar(select(CapacityPlan.id).where(CapacityPlan.brand_id == brand.id).limit(1)):
        return 0

    capacity_specs = [
        (
            date(2026, 8, 3),
            12,
            2,
            3,
            "Publish a verified founder build note if the planned shoot slips.",
            "DEMO · August launch rhythm",
        ),
        (
            date(2026, 10, 5),
            10,
            1,
            2,
            "Use a low-production Builder Walk from the verified proof backlog.",
            "DEMO · October sustainable rhythm",
        ),
        (
            date(2026, 12, 7),
            8,
            1,
            2,
            "Publish the monthly evidence review without adding a new shoot.",
            "DEMO · December reduced capacity",
        ),
    ]
    for week_start, hours, shoots, edits, fallback, notes in capacity_specs:
        db.add(
            CapacityPlan(
                brand_id=brand.id,
                week_start=week_start,
                available_hours=hours,
                max_shoots=shoots,
                max_edits=edits,
                fallback_plan=fallback,
                notes=notes,
                is_demo=True,
            )
        )

    calendar_specs = [
        (
            "DEMO · August BrandOS founder shoot",
            "shoot",
            datetime(2026, 8, 4, 14, tzinfo=UTC),
            2.5,
        ),
        (
            "DEMO · October proof-led editorial review",
            "review",
            datetime(2026, 10, 7, 15, tzinfo=UTC),
            1.5,
        ),
        (
            "DEMO · December Becoming the Evidence edit",
            "edit",
            datetime(2026, 12, 9, 14, tzinfo=UTC),
            2,
        ),
    ]
    for title, event_type, start_at, capacity_units in calendar_specs:
        db.add(
            CalendarEvent(
                brand_id=brand.id,
                title=title,
                event_type=event_type,
                start_at=start_at,
                end_at=start_at + timedelta(hours=capacity_units),
                timezone="America/Toronto",
                capacity_units=capacity_units,
                notes="Visibly labeled seeded demonstration record.",
                is_demo=True,
            )
        )

    script = db.scalar(
        select(Script).where(
            Script.brand_id == brand.id,
            Script.title == "Building my personal Brand OS",
        )
    )
    if script:
        plan = ProductionPlan(
            brand_id=brand.id,
            content_item_id=script.content_item_id,
            script_id=script.id,
            title="DEMO · Building BrandOS founder note",
            creative_treatment=(
                "Phone-first direct-to-camera founder note with restrained interface evidence."
            ),
            equipment=["Smartphone", "Tripod", "Lavalier microphone"],
            wardrobe=["Solid navy layer"],
            props=["Laptop showing the local BrandOS workspace"],
            lighting_plan="Soft window key with warm practical background.",
            music_direction="No music during the proof-led dialogue.",
            estimated_minutes=60,
            status=ProductionStatus.BLOCKED,
            readiness_score=10,
            blockers=[
                "Final script approval is missing",
                "Confirm location",
                "Schedule the shoot",
                "Complete critical checklist",
            ],
            is_demo=True,
        )
        db.add(plan)
        db.flush()
        scene = ProductionScene(
            production_plan_id=plan.id,
            sequence=1,
            title="DEMO · System before motivation",
            purpose="Make the operating-system argument tangible.",
            dialogue=("Consistency is not a personality trait. It is a system design problem."),
            duration_seconds=20,
        )
        db.add(scene)
        db.flush()
        db.add_all(
            [
                ProductionShot(
                    production_scene_id=scene.id,
                    sequence=1,
                    framing="Medium close-up",
                    camera_angle="Eye level",
                    movement="Locked",
                    lighting="Soft window key",
                    instructions="Deliver the approved hook directly to camera.",
                    is_b_roll=False,
                ),
                ProductionShot(
                    production_scene_id=scene.id,
                    sequence=2,
                    framing="Interface detail",
                    camera_angle="Over shoulder",
                    movement="Slow push",
                    lighting="Match display exposure",
                    instructions="Capture the local workflow without exposing secrets.",
                    is_b_roll=True,
                ),
            ]
        )
        db.add_all(
            [
                ProductionChecklistItem(
                    production_plan_id=plan.id,
                    phase="pre_shoot",
                    label="Final script approval recorded",
                    is_critical=True,
                    is_complete=False,
                ),
                ProductionChecklistItem(
                    production_plan_id=plan.id,
                    phase="pre_shoot",
                    label="Location and audio conditions confirmed",
                    is_critical=True,
                    is_complete=False,
                ),
                ProductionChecklistItem(
                    production_plan_id=plan.id,
                    phase="post_shoot",
                    label="Source files copied to two locations",
                    is_critical=True,
                    is_complete=False,
                ),
            ]
        )

        demo_bytes = b"DEMO metadata record; no fabricated media file."
        asset = Asset(
            brand_id=brand.id,
            content_item_id=script.content_item_id,
            production_plan_id=plan.id,
            filename="DEMO-brandos-shot-reference.txt",
            storage_key="demo/assets/brandos-shot-reference.txt",
            media_type="document",
            mime_type="text/plain",
            size_bytes=len(demo_bytes),
            checksum_sha256=hashlib.sha256(demo_bytes).hexdigest(),
            tags=["demo", "production", "reference"],
            rights_status=RightsStatus.UNKNOWN,
            rights_notes="DEMO metadata only; rights intentionally unverified.",
            original_preserved=False,
            is_demo=True,
        )
        db.add(asset)

    db.add(
        ProofItem(
            brand_id=brand.id,
            title="DEMO · Governed BrandOS foundation",
            proof_type="build_log",
            credibility_gap="Can brand operations move from documents into governed records?",
            context="A local-first MVP needed durable provenance and approval boundaries.",
            constraints="No public launch, no fabricated live integrations, and no hidden writes.",
            process=(
                "Imported source documents and built the lifecycle through production planning."
            ),
            output="A connected command center, authoring studio, and readiness workflow.",
            result="DEMO assertion only; live validation is recorded separately in project docs.",
            lessons="Operational truth requires durable evidence and visibly labeled examples.",
            evidence_links=[
                {
                    "label": "DEMO · local validation report",
                    "url": "docs/VALIDATION_REPORT.md",
                }
            ],
            permission_status="not_required",
            sensitivity="internal",
            status=ProofStatus.VERIFIED,
            is_demo=True,
        )
    )
    db.commit()
    return 1


def seed_intelligence(db: Session, brand: Brand) -> int:
    if db.scalar(select(Creator.id).where(Creator.brand_id == brand.id).limit(1)):
        return 0

    creator_specs = [
        (
            "DEMO · Systems Educator",
            "demo-systems-educator",
            "YouTube",
            1,
            8.8,
            ["Build", "Lead"],
            ["Explainer", "Founder note"],
        ),
        (
            "DEMO · AI Builder",
            "demo-ai-builder",
            "LinkedIn",
            2,
            8.4,
            ["Leverage", "Create"],
            ["Build log", "Carousel"],
        ),
        (
            "DEMO · Ownership Teacher",
            "demo-ownership-teacher",
            "Instagram",
            3,
            7.7,
            ["Own"],
            ["Reel", "Visual explainer"],
        ),
    ]
    creators: list[Creator] = []
    for name, username, platform, tier, relevance, pillars, formats in creator_specs:
        creator = Creator(
            brand_id=brand.id,
            name=name,
            username=username,
            platform=platform,
            url=f"https://example.test/{username}",
            category="Builder Intelligence reference",
            why_tracked="DEMO record for exercising the local watchlist and heartbeat.",
            tier=tier,
            relevance_score=relevance,
            content_pillars=pillars,
            formats=formats,
            voice="Clear, practical, and evidence-oriented demo classification.",
            hook_style="Starts with an operational tension.",
            production_style="Simple founder-led framing with restrained visual evidence.",
            audience="Builders and operators",
            last_reviewed_at=datetime(2026, 8, 1, 12, tzinfo=UTC),
            watch_status="active",
            is_demo=True,
        )
        db.add(creator)
        db.flush()
        creators.append(creator)

    benchmark = BenchmarkContent(
        brand_id=brand.id,
        creator_id=creators[0].id,
        source_url="https://example.test/demo-systems-educator/system-before-motivation",
        platform="youtube",
        title="DEMO · System before motivation teardown",
        source_type="seed",
        raw_metadata={"synthetic": True, "external_acquisition": False},
        transcript_excerpt=None,
        hook_analysis="DEMO inference: begin with the cost of relying on motivation.",
        structure_analysis="Tension, mechanism, first-party evidence, next action.",
        visual_analysis="DEMO inference: founder framing plus a concise system diagram.",
        editing_analysis="DEMO inference: deliberate pacing with minimal transition effects.",
        transferable_mechanics=[
            "Name the operational tension before revealing the system",
            "Use first-party evidence to make an abstract workflow tangible",
        ],
        protected_identity=[
            "Do not reuse exact wording, signature identity, or distinctive expression."
        ],
        mezie_adaptations=[
            "Apply the tension-to-system mechanic to original BrandOS readiness evidence."
        ],
        pattern_tags=["systems", "evidence", "founder-led"],
        limitations=[
            "Synthetic demo record; no external creator content was acquired or measured."
        ],
        evidence_level="demo_synthetic",
        status="analyzed",
        is_demo=True,
    )
    db.add(benchmark)
    db.flush()

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
    run = HeartbeatRun(
        brand_id=brand.id,
        run_date=date(2026, 8, 1),
        trigger="seed",
        idempotency_key="demo-heartbeat-2026-08-01",
        status="partial",
        source_coverage=[
            {"source": "demo_watchlist", "status": "synthetic", "records": 3},
            {"source": "external_research", "status": "disabled", "records": 0},
        ],
        model_alias="deterministic_demo",
        tools_used=["database"],
        model_cost=0,
        tool_cost=0,
        records_changed=[],
        errors=["DEMO record; external freshness was not checked."],
        confidence=0.4,
        completed_at=datetime(2026, 8, 1, 13, tzinfo=UTC),
        is_demo=True,
    )
    db.add(run)
    db.flush()
    brief = DailyBrief(
        brand_id=brand.id,
        heartbeat_run_id=run.id,
        brief_date=date(2026, 8, 1),
        title="DEMO · Daily Brand Intelligence · 2026-08-01",
        what_changed=[
            {
                "summary": "Synthetic example: system-led creator formats remain relevant.",
                "classification": "demo_hypothesis",
            }
        ],
        creator_watch=[
            {
                "creator_id": creators[0].id,
                "name": creators[0].name,
                "summary": "Synthetic watchlist example; no live scan occurred.",
            }
        ],
        trend_signals=[],
        content_opportunities=[
            {
                "title": "Why production readiness needs durable blockers",
                "pillar": "Build",
                "series": "Building Creed",
                "classification": "demo_hypothesis",
            }
        ],
        risks_noise=["Do not mistake seeded creator patterns for live performance evidence."],
        recommended_actions=["Run a manual heartbeat after adding real operator evidence."],
        recommended_action="Review the demo structure, then run a source-grounded local brief.",
        coverage_gaps=["External creator activity and trends were not checked."],
        is_demo=True,
    )
    db.add(brief)
    db.flush()
    run.records_changed = [
        {"record_type": "daily_brief", "record_id": brief.id, "action": "seeded"}
    ]

    metric = db.scalar(
        select(MetricSnapshot)
        .where(MetricSnapshot.brand_id == brand.id)
        .order_by(MetricSnapshot.created_at)
    )
    db.add(
        Insight(
            brand_id=brand.id,
            content_item_id=metric.content_item_id if metric else None,
            classification="raw_observation",
            title="DEMO · Saves suggest utility, not causation",
            observation="The seeded X thread records 83 saves and 47 shares.",
            hypothesis=(
                "Practical system language may support saves, but one synthetic record "
                "cannot establish a driver."
            ),
            evidence=[{"metric_snapshot_id": metric.id if metric else None, "synthetic": True}],
            confidence=0.2,
            status="working",
            is_demo=True,
        )
    )
    db.add(
        Experiment(
            brand_id=brand.id,
            title="DEMO · Identity hook versus educational hook",
            question="Do identity-based hooks improve qualified saves for Builder Walks?",
            hypothesis="Identity hooks may improve qualified saves.",
            variable="hook type",
            control_conditions=["Same topic", "Same duration", "Same production quality"],
            platform="Instagram",
            content_type="Builder Walk",
            expected_outcome="A measurable difference in save rate.",
            success_metric="Save rate",
            measurement_start=date(2026, 9, 1),
            measurement_end=date(2026, 9, 21),
            status="planned",
            confidence=0,
            is_demo=True,
        )
    )
    db.commit()
    return 1


def seed_database(db: Session, source_root: Path | None = None) -> dict[str, int]:
    brand = seed_brand(db)
    resolved_source_root = source_root or resolve_source_root()
    imported = import_documents(db, brand, resolved_source_root)
    skills_imported = import_skill_definitions(db, resolved_source_root)
    seed_workspace(db, brand)
    authoring_seeded = seed_authoring(db, brand)
    planning_seeded = seed_planning_and_proof(db, brand)
    intelligence_seeded = seed_intelligence(db, brand)
    return {
        "documents_imported": imported,
        "skills_imported": skills_imported,
        "authoring_seeded": authoring_seeded,
        "planning_seeded": planning_seeded,
        "intelligence_seeded": intelligence_seeded,
    }


def main() -> None:
    with SessionLocal() as db:
        result = seed_database(db)
    print(
        "Seed complete: "
        f"{result['documents_imported']} source documents and "
        f"{result['skills_imported']} skill definitions imported; "
        f"{result['authoring_seeded']} authoring workspace and "
        f"{result['planning_seeded']} planning workspace; "
        f"{result['intelligence_seeded']} intelligence workspace seeded."
    )


if __name__ == "__main__":
    main()
