from __future__ import annotations

import re
from datetime import UTC, date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import UserPrincipal
from app.db.models import (
    ApprovalStatus,
    Brand,
    CalendarEvent,
    CapacityPlan,
    ContentItem,
    PipelineEvent,
    PipelineStatus,
    ProductionChecklistItem,
    ProductionPlan,
    ProductionScene,
    ProductionShot,
    ProductionStatus,
    Script,
    ScriptStatus,
    ScriptVersion,
)
from app.schemas.contracts import (
    CalendarEventCreate,
    CapacityPlanCreate,
    ChecklistItemView,
    ProductionPlanUpdate,
    ProductionPlanView,
    ProductionSceneView,
    ProductionShotView,
)


def _active_brand(db: Session) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.is_active.is_(True)))
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active brand missing.",
        )
    return brand


def monday_for(value: date) -> date:
    return value - timedelta(days=value.weekday())


def upsert_capacity(
    db: Session,
    payload: CapacityPlanCreate,
) -> CapacityPlan:
    brand = _active_brand(db)
    week_start = monday_for(payload.week_start)
    capacity = db.scalar(
        select(CapacityPlan).where(
            CapacityPlan.brand_id == brand.id,
            CapacityPlan.week_start == week_start,
        )
    )
    if capacity:
        for field, value in payload.model_dump().items():
            setattr(capacity, field, value)
        capacity.week_start = week_start
    else:
        capacity = CapacityPlan(
            brand_id=brand.id,
            **payload.model_dump(exclude={"week_start"}),
            week_start=week_start,
        )
        db.add(capacity)
    db.commit()
    db.refresh(capacity)
    return capacity


def capacity_for_week(db: Session, brand_id: str, week_start: date) -> CapacityPlan:
    normalized = monday_for(week_start)
    capacity = db.scalar(
        select(CapacityPlan).where(
            CapacityPlan.brand_id == brand_id,
            CapacityPlan.week_start == normalized,
        )
    )
    if capacity:
        return capacity
    capacity = CapacityPlan(
        brand_id=brand_id,
        week_start=normalized,
        available_hours=10,
        max_shoots=2,
        max_edits=3,
        fallback_plan="Publish one low-production proof note if the planned shoot slips.",
    )
    db.add(capacity)
    db.flush()
    return capacity


def create_calendar_event(
    db: Session,
    payload: CalendarEventCreate,
) -> CalendarEvent:
    brand = _active_brand(db)
    if payload.end_at <= payload.start_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Calendar event end must be after its start.",
        )
    if payload.content_item_id and not db.get(ContentItem, payload.content_item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked content item not found.",
        )
    week_start = monday_for(payload.start_at.date())
    capacity = capacity_for_week(db, brand.id, week_start)
    week_start_at = datetime.combine(week_start, time.min, tzinfo=UTC)
    week_end_at = week_start_at + timedelta(days=7)
    events = list(
        db.scalars(
            select(CalendarEvent).where(
                CalendarEvent.brand_id == brand.id,
                CalendarEvent.start_at >= week_start_at,
                CalendarEvent.start_at < week_end_at,
                CalendarEvent.status != "cancelled",
            )
        ).all()
    )
    projected_hours = sum(item.capacity_units for item in events) + payload.capacity_units
    if projected_hours > capacity.available_hours:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Weekly capacity exceeded: {projected_hours:.1f} requested "
                f"against {capacity.available_hours:.1f} available hours."
            ),
        )
    type_count = sum(item.event_type == payload.event_type for item in events)
    if payload.event_type == "shoot" and type_count >= capacity.max_shoots:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Weekly shoot capacity is already full.",
        )
    if payload.event_type == "edit" and type_count >= capacity.max_edits:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Weekly edit capacity is already full.",
        )
    event = CalendarEvent(
        brand_id=brand.id,
        **payload.model_dump(),
        status="planned",
        is_demo=False,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _script_scenes(version: ScriptVersion, cta: str) -> list[tuple[str, str, str]]:
    sentences = [
        item.strip() for item in re.split(r"(?<=[.!?])\s+", version.body_text) if item.strip()
    ]
    midpoint = max(1, len(sentences) // 2)
    opening = sentences[:1] or [version.hook_selected]
    development = sentences[1:midpoint] or sentences[1:] or [version.body_text]
    evidence = sentences[midpoint:] or [version.body_text]
    return [
        ("Hook", "Earn attention with a clear builder tension.", " ".join(opening)),
        (
            "Build",
            "Develop the useful argument and show the operating logic.",
            " ".join(development),
        ),
        (
            "Evidence and CTA",
            "Close with proof, a practical next action, and the CTA.",
            f"{' '.join(evidence)} {cta}",
        ),
    ]


def create_production_plan(
    db: Session,
    script: Script,
    user: UserPrincipal,
) -> ProductionPlan:
    existing = db.scalar(select(ProductionPlan).where(ProductionPlan.script_id == script.id))
    if existing:
        return existing
    if script.status != ScriptStatus.APPROVED or script.approval_status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An approved final script is required for production planning.",
        )
    version = db.get(ScriptVersion, script.current_version_id)
    content = db.get(ContentItem, script.content_item_id)
    if not version or not content:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The approved script is missing its active version or content item.",
        )
    plan = ProductionPlan(
        brand_id=script.brand_id,
        content_item_id=content.id,
        script_id=script.id,
        title=script.title,
        creative_treatment=(
            "Founder-led editorial execution: direct-to-camera clarity, restrained motion, "
            "warm practical light, and product evidence used only where verified."
        ),
        equipment=["Smartphone or camera", "Tripod", "Lavalier microphone"],
        wardrobe=["Solid neutral layer", "No distracting logos"],
        props=["Laptop with BrandOS local workspace"],
        lighting_plan="Soft key at 45 degrees with a practical warm background source.",
        music_direction="Minimal instrumental bed; dialogue remains dominant.",
        estimated_minutes=max(45, version.duration_seconds * 2),
        blockers=["Confirm location", "Schedule the shoot", "Complete critical checklist"],
        status=ProductionStatus.BLOCKED,
        is_demo=script.is_demo,
    )
    db.add(plan)
    db.flush()
    scenes = _script_scenes(version, version.cta)
    per_scene = max(10, version.duration_seconds // len(scenes))
    for sequence, (title, purpose, dialogue) in enumerate(scenes, 1):
        scene = ProductionScene(
            production_plan_id=plan.id,
            sequence=sequence,
            title=title,
            purpose=purpose,
            dialogue=dialogue,
            duration_seconds=per_scene,
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
                    lighting="Soft key and practical background",
                    instructions=f"Deliver {title.lower()} directly to camera.",
                    is_b_roll=False,
                ),
                ProductionShot(
                    production_scene_id=scene.id,
                    sequence=2,
                    framing="Detail insert",
                    camera_angle="Over shoulder",
                    movement="Slow controlled push",
                    lighting="Match primary scene exposure",
                    instructions="Capture product or notebook evidence that supports the dialogue.",
                    is_b_roll=True,
                ),
            ]
        )
    checklist = [
        ("pre_shoot", "Final script approval recorded", True, True),
        ("pre_shoot", "Location confirmed and quiet", True, False),
        ("pre_shoot", "Camera and audio batteries charged", True, False),
        ("pre_shoot", "Storage cleared and backup path ready", True, False),
        ("pre_shoot", "Wardrobe and props staged", False, False),
        ("post_shoot", "Primary dialogue reviewed for focus and audio", True, False),
        ("post_shoot", "Files copied to two locations", True, False),
        ("post_shoot", "Missing shots logged before teardown", False, False),
    ]
    for phase, label, critical, complete in checklist:
        db.add(
            ProductionChecklistItem(
                production_plan_id=plan.id,
                phase=phase,
                label=label,
                is_critical=critical,
                is_complete=complete,
                completed_at=datetime.now(UTC) if complete else None,
            )
        )
    db.flush()
    recalculate_readiness(db, plan, user.username)
    db.commit()
    db.refresh(plan)
    return plan


def recalculate_readiness(
    db: Session,
    plan: ProductionPlan,
    actor: str,
) -> ProductionPlan:
    script = db.get(Script, plan.script_id)
    content = db.get(ContentItem, plan.content_item_id)
    checklist = list(
        db.scalars(
            select(ProductionChecklistItem).where(
                ProductionChecklistItem.production_plan_id == plan.id
            )
        ).all()
    )
    critical = [item for item in checklist if item.is_critical and item.phase == "pre_shoot"]
    critical_complete = (
        sum(item.is_complete for item in critical) / len(critical) if critical else 1
    )
    blockers: list[str] = []
    score = 0.0
    if script and script.approval_status == ApprovalStatus.APPROVED:
        score += 20
    else:
        blockers.append("Final script approval is missing")
    if plan.scheduled_at:
        score += 15
    else:
        blockers.append("Schedule the shoot")
    if plan.location:
        score += 10
    else:
        blockers.append("Confirm location")
    if plan.equipment:
        score += 10
    else:
        blockers.append("Equipment list is empty")
    score += critical_complete * 45
    incomplete_critical = [item.label for item in critical if not item.is_complete]
    if incomplete_critical:
        blockers.append(f"{len(incomplete_critical)} critical checklist items remain")
    plan.readiness_score = round(min(100, score), 1)
    plan.blockers = blockers
    plan.status = ProductionStatus.READY if not blockers else ProductionStatus.BLOCKED
    if (
        not blockers
        and content
        and content.status == PipelineStatus.APPROVED
        and content.approval_status == ApprovalStatus.APPROVED
    ):
        db.add(
            PipelineEvent(
                content_item_id=content.id,
                from_status=content.status.value,
                to_status=PipelineStatus.READY_TO_SHOOT.value,
                actor=actor,
                reason="Production plan reached 100% readiness.",
            )
        )
        content.status = PipelineStatus.READY_TO_SHOOT
        content.readiness_score = 100
    return plan


def update_production_plan(
    db: Session,
    plan: ProductionPlan,
    payload: ProductionPlanUpdate,
    user: UserPrincipal,
) -> ProductionPlan:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    recalculate_readiness(db, plan, user.username)
    db.commit()
    db.refresh(plan)
    return plan


def toggle_checklist_item(
    db: Session,
    item: ProductionChecklistItem,
    complete: bool,
    user: UserPrincipal,
) -> ProductionPlan:
    item.is_complete = complete
    item.completed_at = datetime.now(UTC) if complete else None
    plan = db.get(ProductionPlan, item.production_plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production plan not found.",
        )
    recalculate_readiness(db, plan, user.username)
    db.commit()
    db.refresh(plan)
    return plan


def production_plan_view(db: Session, plan: ProductionPlan) -> ProductionPlanView:
    scenes = list(
        db.scalars(
            select(ProductionScene)
            .where(ProductionScene.production_plan_id == plan.id)
            .order_by(ProductionScene.sequence)
        ).all()
    )
    scene_ids = [scene.id for scene in scenes]
    shots = (
        list(
            db.scalars(
                select(ProductionShot)
                .where(ProductionShot.production_scene_id.in_(scene_ids))
                .order_by(ProductionShot.production_scene_id, ProductionShot.sequence)
            ).all()
        )
        if scene_ids
        else []
    )
    checklist = list(
        db.scalars(
            select(ProductionChecklistItem)
            .where(ProductionChecklistItem.production_plan_id == plan.id)
            .order_by(
                ProductionChecklistItem.phase,
                ProductionChecklistItem.is_critical.desc(),
                ProductionChecklistItem.created_at,
            )
        ).all()
    )
    return ProductionPlanView.model_validate(
        {
            **{
                key: getattr(plan, key)
                for key in (
                    "id",
                    "content_item_id",
                    "script_id",
                    "title",
                    "creative_treatment",
                    "location",
                    "equipment",
                    "wardrobe",
                    "props",
                    "lighting_plan",
                    "music_direction",
                    "scheduled_at",
                    "estimated_minutes",
                    "status",
                    "readiness_score",
                    "blockers",
                    "is_demo",
                    "created_at",
                    "updated_at",
                )
            },
            "scenes": [ProductionSceneView.model_validate(item) for item in scenes],
            "shots": [ProductionShotView.model_validate(item) for item in shots],
            "checklist": [ChecklistItemView.model_validate(item) for item in checklist],
        }
    )
