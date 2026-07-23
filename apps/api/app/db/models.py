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
