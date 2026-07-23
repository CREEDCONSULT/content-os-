from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CanonicalStatus(StrEnum):
    CANONICAL = "canonical"
    WORKING = "working"
    ARCHIVED = "archived"
    RESTRICTED = "restricted"


class IdeaStatus(StrEnum):
    CAPTURED = "captured"
    CLARIFYING = "clarifying"
    RESEARCHING = "researching"
    SELECTED = "selected"
    CONVERTED_TO_BRIEF = "converted_to_brief"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class PipelineStatus(StrEnum):
    IDEA = "idea"
    RESEARCH = "research"
    BRIEF = "brief"
    SCRIPT = "script"
    REVIEW = "review"
    APPROVED = "approved"
    READY_TO_SHOOT = "ready_to_shoot"
    SHOT = "shot"
    EDITING = "editing"
    REVIEW_EDIT = "review_edit"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHED = "published"
    ANALYTICS_REVIEW = "analytics_review"
    REPURPOSE = "repurpose"
    ARCHIVED = "archived"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BriefStatus(StrEnum):
    DRAFT = "draft"
    PROOF_NEEDED = "proof_needed"
    READY = "ready"
    ARCHIVED = "archived"


class ScriptStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ReviewStatus(StrEnum):
    NOT_STARTED = "not_started"
    NEEDS_REVIEW = "needs_review"
    VERIFIED = "verified"
    BLOCKED = "blocked"


class ProductionStatus(StrEnum):
    DRAFT = "draft"
    BLOCKED = "blocked"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class RightsStatus(StrEnum):
    UNKNOWN = "unknown"
    OWNED = "owned"
    LICENSED = "licensed"
    RESTRICTED = "restricted"


class ProofStatus(StrEnum):
    DRAFT = "draft"
    EVIDENCE_NEEDED = "evidence_needed"
    VERIFIED = "verified"
    APPROVED = "approved"
    ARCHIVED = "archived"


class Timestamped:
    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Brand(Timestamped, Base):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    founder_name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    positioning: Mapped[str] = mapped_column(Text, nullable=False)
    signature_line: Mapped[str] = mapped_column(String(240), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BrandDocument(Timestamped, Base):
    __tablename__ = "brand_documents"
    __table_args__ = (UniqueConstraint("brand_id", "slug"),)

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    slug: Mapped[str] = mapped_column(String(240), nullable=False)
    canonical_status: Mapped[CanonicalStatus] = mapped_column(
        Enum(CanonicalStatus, native_enum=False), default=CanonicalStatus.WORKING, index=True
    )
    current_version_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    source_path: Mapped[str | None] = mapped_column(String(800))
    vault_path: Mapped[str | None] = mapped_column(String(800))
    sensitivity: Mapped[str] = mapped_column(String(40), default="internal")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    version_count: Mapped[int] = mapped_column(Integer, default=0)


class BrandDocumentVersion(Timestamped, Base):
    __tablename__ = "brand_document_versions"
    __table_args__ = (UniqueConstraint("brand_document_id", "version_number"),)

    brand_document_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("brand_documents.id"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    approval_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class Idea(Timestamped, Base):
    __tablename__ = "ideas"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), default="dashboard", index=True)
    source_reference: Mapped[str | None] = mapped_column(String(800))
    pillar: Mapped[str | None] = mapped_column(String(80), index=True)
    series: Mapped[str | None] = mapped_column(String(120), index=True)
    audience: Mapped[str] = mapped_column(String(160), default="Emerging Builder")
    platform_fit: Mapped[list[str]] = mapped_column(JSON, default=list)
    strategic_objective: Mapped[str | None] = mapped_column(String(240))
    urgency: Mapped[str] = mapped_column(String(40), default="normal")
    status: Mapped[IdeaStatus] = mapped_column(
        Enum(IdeaStatus, native_enum=False), default=IdeaStatus.CAPTURED, index=True
    )
    brand_fit_score: Mapped[float] = mapped_column(Float, default=0)
    audience_value_score: Mapped[float] = mapped_column(Float, default=0)
    proof_score: Mapped[float] = mapped_column(Float, default=0)
    timeliness_score: Mapped[float] = mapped_column(Float, default=0)
    originality_score: Mapped[float] = mapped_column(Float, default=0)
    feasibility_score: Mapped[float] = mapped_column(Float, default=0)
    strategic_importance_score: Mapped[float] = mapped_column(Float, default=0)
    total_priority_score: Mapped[float] = mapped_column(Float, default=0, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ContentItem(Timestamped, Base):
    __tablename__ = "content_items"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    idea_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey("ideas.id"))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    platform: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(80), nullable=False)
    pillar: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    series: Mapped[str | None] = mapped_column(String(120))
    audience: Mapped[str] = mapped_column(String(160), default="Emerging Builder")
    objective: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus, native_enum=False), default=PipelineStatus.IDEA, index=True
    )
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    due_date: Mapped[date | None] = mapped_column(Date)
    publish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    publication_url: Mapped[str | None] = mapped_column(String(800))
    readiness_score: Mapped[float] = mapped_column(Float, default=0)
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False), default=ApprovalStatus.NOT_REQUIRED
    )
    blocker: Mapped[str | None] = mapped_column(String(500))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ContentBrief(Timestamped, Base):
    __tablename__ = "content_briefs"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    idea_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("ideas.id"), unique=True, index=True
    )
    content_item_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    objective: Mapped[str] = mapped_column(String(500), nullable=False)
    audience: Mapped[str] = mapped_column(String(160), nullable=False)
    platform: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(80), nullable=False)
    pillar: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    series: Mapped[str | None] = mapped_column(String(120))
    core_message: Mapped[str] = mapped_column(Text, nullable=False)
    audience_problem: Mapped[str] = mapped_column(Text, nullable=False)
    desired_emotion: Mapped[str] = mapped_column(String(120), nullable=False)
    desired_action: Mapped[str] = mapped_column(String(240), nullable=False)
    proof_points: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    benchmark_references: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    visual_direction: Mapped[str] = mapped_column(Text, nullable=False)
    production_constraints: Mapped[list[str]] = mapped_column(JSON, default=list)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=60)
    cta: Mapped[str] = mapped_column(String(500), nullable=False)
    success_metric: Mapped[str] = mapped_column(String(240), nullable=False)
    evidence_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        default=ReviewStatus.NEEDS_REVIEW,
        index=True,
    )
    status: Mapped[BriefStatus] = mapped_column(
        Enum(BriefStatus, native_enum=False),
        default=BriefStatus.DRAFT,
        index=True,
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class Script(Timestamped, Base):
    __tablename__ = "scripts"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_brief_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_briefs.id"), unique=True, index=True
    )
    content_item_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[ScriptStatus] = mapped_column(
        Enum(ScriptStatus, native_enum=False),
        default=ScriptStatus.DRAFT,
        index=True,
    )
    current_version_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    version_count: Mapped[int] = mapped_column(Integer, default=0)
    fact_check_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        default=ReviewStatus.NOT_STARTED,
        index=True,
    )
    financial_risk: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, native_enum=False),
        default=RiskLevel.LOW,
        index=True,
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False),
        default=ApprovalStatus.NOT_REQUIRED,
        index=True,
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ScriptVersion(Timestamped, Base):
    __tablename__ = "script_versions"
    __table_args__ = (UniqueConstraint("script_id", "version_number"),)

    script_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("scripts.id"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    hook_selected: Mapped[str] = mapped_column(Text, nullable=False)
    on_screen_text: Mapped[list[str]] = mapped_column(JSON, default=list)
    b_roll_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    camera_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    cta: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    brand_alignment_score: Mapped[float] = mapped_column(Float, default=0)
    originality_score: Mapped[float] = mapped_column(Float, default=0)
    evidence_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    change_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    approval_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class HookOption(Timestamped, Base):
    __tablename__ = "hook_options"

    script_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("script_versions.id"), index=True
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    clarity_score: Mapped[float] = mapped_column(Float, default=0)
    curiosity_score: Mapped[float] = mapped_column(Float, default=0)
    specificity_score: Mapped[float] = mapped_column(Float, default=0)
    brand_fit_score: Mapped[float] = mapped_column(Float, default=0)
    audience_fit_score: Mapped[float] = mapped_column(Float, default=0)
    originality_score: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0, index=True)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    fatigue_warning: Mapped[str | None] = mapped_column(String(500))


class FactCheck(Timestamped, Base):
    __tablename__ = "fact_checks"

    script_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("script_versions.id"), unique=True, index=True
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, native_enum=False),
        default=ReviewStatus.NEEDS_REVIEW,
        index=True,
    )
    claim_table: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    unresolved_claims: Mapped[list[str]] = mapped_column(JSON, default=list)
    verified_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    financial_classification: Mapped[str] = mapped_column(String(80), default="not_financial")
    blocked_claims: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_disclosures: Mapped[list[str]] = mapped_column(JSON, default=list)
    reviewed_by: Mapped[str] = mapped_column(String(120), nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class CapacityPlan(Timestamped, Base):
    __tablename__ = "capacity_plans"
    __table_args__ = (UniqueConstraint("brand_id", "week_start"),)

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    available_hours: Mapped[float] = mapped_column(Float, default=10)
    max_shoots: Mapped[int] = mapped_column(Integer, default=2)
    max_edits: Mapped[int] = mapped_column(Integer, default=3)
    fallback_plan: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class CalendarEvent(Timestamped, Base):
    __tablename__ = "calendar_events"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_item_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="America/Toronto")
    status: Mapped[str] = mapped_column(String(40), default="planned", index=True)
    capacity_units: Mapped[float] = mapped_column(Float, default=1)
    notes: Mapped[str | None] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ProductionPlan(Timestamped, Base):
    __tablename__ = "production_plans"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_item_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), unique=True, index=True
    )
    script_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("scripts.id"), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    creative_treatment: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(240))
    equipment: Mapped[list[str]] = mapped_column(JSON, default=list)
    wardrobe: Mapped[list[str]] = mapped_column(JSON, default=list)
    props: Mapped[list[str]] = mapped_column(JSON, default=list)
    lighting_plan: Mapped[str] = mapped_column(Text, nullable=False)
    music_direction: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[ProductionStatus] = mapped_column(
        Enum(ProductionStatus, native_enum=False),
        default=ProductionStatus.DRAFT,
        index=True,
    )
    readiness_score: Mapped[float] = mapped_column(Float, default=0)
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ProductionScene(Timestamped, Base):
    __tablename__ = "production_scenes"
    __table_args__ = (UniqueConstraint("production_plan_id", "sequence"),)

    production_plan_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("production_plans.id"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    purpose: Mapped[str] = mapped_column(String(500), nullable=False)
    dialogue: Mapped[str] = mapped_column(Text, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)


class ProductionShot(Timestamped, Base):
    __tablename__ = "production_shots"
    __table_args__ = (UniqueConstraint("production_scene_id", "sequence"),)

    production_scene_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("production_scenes.id"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    framing: Mapped[str] = mapped_column(String(120), nullable=False)
    camera_angle: Mapped[str] = mapped_column(String(120), nullable=False)
    movement: Mapped[str] = mapped_column(String(120), nullable=False)
    lighting: Mapped[str] = mapped_column(String(240), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    is_b_roll: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(40), default="planned", index=True)


class ProductionChecklistItem(Timestamped, Base):
    __tablename__ = "production_checklist_items"

    production_plan_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("production_plans.id"), index=True
    )
    phase: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Asset(Timestamped, Base):
    __tablename__ = "assets"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_item_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), index=True
    )
    production_plan_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("production_plans.id"), index=True
    )
    filename: Mapped[str] = mapped_column(String(240), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(800), unique=True, nullable=False)
    media_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(160), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    people: Mapped[list[str]] = mapped_column(JSON, default=list)
    location: Mapped[str | None] = mapped_column(String(240))
    orientation: Mapped[str | None] = mapped_column(String(40))
    quality_score: Mapped[float] = mapped_column(Float, default=0)
    rights_status: Mapped[RightsStatus] = mapped_column(
        Enum(RightsStatus, native_enum=False),
        default=RightsStatus.UNKNOWN,
        index=True,
    )
    rights_notes: Mapped[str | None] = mapped_column(Text)
    original_preserved: Mapped[bool] = mapped_column(Boolean, default=True)
    duplicate_of_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ProofItem(Timestamped, Base):
    __tablename__ = "proof_items"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_item_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    proof_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    credibility_gap: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, nullable=False)
    process: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    lessons: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_links: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    asset_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    permission_status: Mapped[str] = mapped_column(String(60), default="not_required", index=True)
    sensitivity: Mapped[str] = mapped_column(String(60), default="internal")
    status: Mapped[ProofStatus] = mapped_column(
        Enum(ProofStatus, native_enum=False),
        default=ProofStatus.EVIDENCE_NEEDED,
        index=True,
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class PipelineEvent(Timestamped, Base):
    __tablename__ = "pipeline_events"

    content_item_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), index=True
    )
    from_status: Mapped[str] = mapped_column(String(40), nullable=False)
    to_status: Mapped[str] = mapped_column(String(40), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))


class Approval(Timestamped, Base):
    __tablename__ = "approvals"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(100), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True)
    target_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), index=True)
    requested_by: Mapped[str] = mapped_column(String(120), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, native_enum=False), index=True)
    cost_estimate: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False), default=ApprovalStatus.PENDING, index=True
    )
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    approved_by: Mapped[str | None] = mapped_column(String(120))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class Task(Timestamped, Base):
    __tablename__ = "tasks"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(40), default="todo", index=True)
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    related_type: Mapped[str | None] = mapped_column(String(80))
    related_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class MetricSnapshot(Timestamped, Base):
    __tablename__ = "metric_snapshots"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    content_item_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("content_items.id"), index=True
    )
    platform: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    views: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    watch_time_seconds: Mapped[float] = mapped_column(Float, default=0)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class SkillDefinition(Timestamped, Base):
    __tablename__ = "skill_definitions"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    version: Mapped[str] = mapped_column(String(40), default="1.0.0", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_summary: Mapped[str] = mapped_column(Text, nullable=False)
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    required_context: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_tools: Mapped[list[str]] = mapped_column(JSON, default=list)
    workflow: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    memory_policy: Mapped[str] = mapped_column(Text, nullable=False)
    approval_policy: Mapped[str] = mapped_column(Text, nullable=False)
    failure_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    model_profile: Mapped[str] = mapped_column(String(80), default="brand_fast_model")
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=120)
    cost_class: Mapped[str] = mapped_column(String(30), default="low")
    source_path: Mapped[str] = mapped_column(String(800), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)


class ContextPack(Timestamped, Base):
    __tablename__ = "context_packs"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    intent: Mapped[str] = mapped_column(String(500), nullable=False)
    source_records: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    context_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    freshness_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    exclusions: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="ready", index=True)


class AgentRun(Timestamped, Base):
    __tablename__ = "agent_runs"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    request_id: Mapped[str] = mapped_column(
        String(80), default=lambda: str(uuid.uuid4()), nullable=False, index=True
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(160), unique=True, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    intent: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(40), default="mock", nullable=False)
    model_alias: Mapped[str] = mapped_column(String(100), nullable=False)
    context_pack_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("context_packs.id"), index=True
    )
    skills_used: Mapped[list[str]] = mapped_column(JSON, default=list)
    tools_used: Mapped[list[str]] = mapped_column(JSON, default=list)
    context_loaded: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    input_envelope: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_envelope: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    model_cost: Mapped[float] = mapped_column(Float, default=0)
    tool_cost: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_writes: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    completed_writes: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    approvals_required: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    next_actions: Mapped[list[str]] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditEvent(Timestamped, Base):
    __tablename__ = "audit_events"

    brand_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("brands.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


Index("ix_ideas_brand_status_score", Idea.brand_id, Idea.status, Idea.total_priority_score)
Index("ix_content_brand_status_due", ContentItem.brand_id, ContentItem.status, ContentItem.due_date)
