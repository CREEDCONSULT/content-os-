from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import ApprovalStatus, CanonicalStatus, IdeaStatus, PipelineStatus, RiskLevel


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=500)


class AuthUser(BaseModel):
    username: str
    display_name: str
    permissions: list[str]


class AuthResponse(BaseModel):
    user: AuthUser
    expires_in: int


class BrandDocumentSummary(ORMModel):
    id: str
    document_type: str
    title: str
    slug: str
    canonical_status: CanonicalStatus
    source_path: str | None
    vault_path: str | None
    sensitivity: str
    tags: list[str]
    version_count: int
    updated_at: datetime


class BrandDocumentVersionView(ORMModel):
    id: str
    brand_document_id: str
    version_number: int
    content_markdown: str
    change_summary: str
    checksum_sha256: str
    provenance: dict[str, Any]
    created_by: str
    approval_id: str | None
    is_active: bool
    created_at: datetime


class BrandDocumentDetail(BrandDocumentSummary):
    current_version: BrandDocumentVersionView | None


class CreateDocumentVersion(BaseModel):
    content_markdown: str = Field(min_length=1)
    change_summary: str = Field(min_length=3, max_length=1000)


class VersionCreationResult(BaseModel):
    version: BrandDocumentVersionView
    approval_id: str | None
    activated: bool


class IdeaScores(BaseModel):
    brand_fit_score: float = Field(ge=0, le=10)
    audience_value_score: float = Field(ge=0, le=10)
    proof_score: float = Field(ge=0, le=10)
    timeliness_score: float = Field(ge=0, le=10)
    originality_score: float = Field(ge=0, le=10)
    feasibility_score: float = Field(ge=0, le=10)
    strategic_importance_score: float = Field(ge=0, le=10)


class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    raw_input: str = Field(min_length=3, max_length=20_000)
    source_type: str = Field(default="dashboard", max_length=40)
    source_reference: str | None = Field(default=None, max_length=800)
    pillar: str | None = Field(default=None, max_length=80)
    series: str | None = Field(default=None, max_length=120)
    audience: str = Field(default="Emerging Builder", max_length=160)
    platform_fit: list[str] = Field(default_factory=list, max_length=8)
    strategic_objective: str | None = Field(default=None, max_length=240)
    urgency: str = Field(default="normal", max_length=40)

    @field_validator("platform_fit")
    @classmethod
    def unique_platforms(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in value if item.strip()))


class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=240)
    raw_input: str | None = Field(default=None, min_length=3, max_length=20_000)
    pillar: str | None = Field(default=None, max_length=80)
    series: str | None = Field(default=None, max_length=120)
    audience: str | None = Field(default=None, max_length=160)
    platform_fit: list[str] | None = None
    strategic_objective: str | None = Field(default=None, max_length=240)
    urgency: str | None = Field(default=None, max_length=40)
    status: IdeaStatus | None = None
    rejection_reason: str | None = Field(default=None, max_length=2000)


class IdeaView(ORMModel):
    id: str
    title: str
    raw_input: str
    source_type: str
    source_reference: str | None
    pillar: str | None
    series: str | None
    audience: str
    platform_fit: list[str]
    strategic_objective: str | None
    urgency: str
    status: IdeaStatus
    brand_fit_score: float
    audience_value_score: float
    proof_score: float
    timeliness_score: float
    originality_score: float
    feasibility_score: float
    strategic_importance_score: float
    total_priority_score: float
    rejection_reason: str | None
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class IdeaList(BaseModel):
    items: list[IdeaView]
    total: int


class ContentView(ORMModel):
    id: str
    idea_id: str | None
    title: str
    platform: str
    format: str
    pillar: str
    series: str | None
    audience: str
    objective: str
    status: PipelineStatus
    priority: str
    due_date: date | None
    publish_at: datetime | None
    readiness_score: float
    approval_status: ApprovalStatus
    blocker: str | None
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class ContentList(BaseModel):
    items: list[ContentView]
    total: int
    groups: dict[str, int]


class ContentTransition(BaseModel):
    to_status: PipelineStatus
    reason: str | None = Field(default=None, max_length=500)


class ApprovalView(ORMModel):
    id: str
    action_type: str
    target_type: str
    target_id: str
    requested_by: str
    risk_level: RiskLevel
    cost_estimate: float
    status: ApprovalStatus
    context: dict[str, Any]
    approved_by: str | None
    decided_at: datetime | None
    notes: str | None
    created_at: datetime


class ApprovalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    notes: str | None = Field(default=None, max_length=2000)


class DashboardMetric(BaseModel):
    label: str
    value: int | float | str
    delta: str | None = None
    accent: str
    is_demo: bool = False


class DashboardTask(BaseModel):
    id: str
    title: str
    due_at: datetime | None
    priority: str
    status: str


class DashboardActivity(BaseModel):
    id: str
    event_type: str
    summary: str
    created_at: datetime
    is_demo: bool


class DashboardUpcoming(BaseModel):
    id: str
    title: str
    platform: str
    due_date: date | None
    status: PipelineStatus


class AgentStatus(BaseModel):
    status: str
    model_alias: str
    current_focus: str
    last_run_at: datetime | None
    is_mock: bool


class DashboardSummary(BaseModel):
    greeting_name: str
    brand_name: str
    signature_line: str
    metrics: list[DashboardMetric]
    pipeline_groups: dict[str, int]
    today: list[DashboardTask]
    recent_activity: list[DashboardActivity]
    upcoming_content: list[DashboardUpcoming]
    pending_approvals: int
    agent: AgentStatus


class IntegrationState(BaseModel):
    id: str
    label: str
    state: str
    detail: str
    last_checked_at: datetime
    server_side_only: bool = True


class IntegrationList(BaseModel):
    items: list[IntegrationState]
