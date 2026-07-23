from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import (
    ApprovalStatus,
    BriefStatus,
    CanonicalStatus,
    IdeaStatus,
    PipelineStatus,
    ProductionStatus,
    ProofStatus,
    ReviewStatus,
    RightsStatus,
    RiskLevel,
    ScriptStatus,
)


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


class AgentBudget(BaseModel):
    model_usd: float = Field(default=0, ge=0, le=100)
    tool_usd: float = Field(default=0, ge=0, le=100)


class AgentRunCreate(BaseModel):
    request_id: str | None = Field(default=None, max_length=80)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=160)
    channel: str = Field(default="dashboard", pattern="^(dashboard|telegram|heartbeat|api)$")
    intent: str = Field(min_length=3, max_length=240)
    raw_input: dict[str, Any] = Field(default_factory=dict)
    budget: AgentBudget = Field(default_factory=AgentBudget)


class SkillDefinitionView(ORMModel):
    id: str
    slug: str
    name: str
    version: str
    description: str
    trigger_summary: str
    input_schema: dict[str, Any]
    required_context: list[str]
    allowed_tools: list[str]
    workflow: list[str]
    output_schema: dict[str, Any]
    memory_policy: str
    approval_policy: str
    failure_behavior: str
    model_profile: str
    timeout_seconds: int
    cost_class: str
    source_path: str
    enabled: bool


class ContextPackView(ORMModel):
    id: str
    intent: str
    source_records: list[dict[str, Any]]
    context_markdown: str
    token_estimate: int
    freshness_notes: list[str]
    exclusions: list[str]
    status: str
    created_at: datetime


class AgentRunView(ORMModel):
    id: str
    request_id: str
    idempotency_key: str | None
    channel: str
    intent: str
    status: str
    provider: str
    model_alias: str
    context_pack_id: str | None
    skills_used: list[str]
    tools_used: list[str]
    context_loaded: list[dict[str, Any]]
    input_envelope: dict[str, Any]
    output_envelope: dict[str, Any]
    model_cost: float
    tool_cost: float
    confidence: float
    summary: str
    proposed_writes: list[dict[str, Any]]
    completed_writes: list[dict[str, Any]]
    approvals_required: list[dict[str, Any]]
    next_actions: list[str]
    error: str | None
    completed_at: datetime | None
    is_demo: bool
    created_at: datetime


class AgentRunList(BaseModel):
    items: list[AgentRunView]
    total: int


class BriefFromIdea(BaseModel):
    platform: str = Field(default="LinkedIn", min_length=2, max_length=60)
    format: str = Field(default="Post", min_length=2, max_length=80)
    objective: str | None = Field(default=None, max_length=500)
    audience_problem: str | None = Field(default=None, max_length=2000)
    desired_emotion: str = Field(default="clarity and agency", max_length=120)
    desired_action: str = Field(
        default="Save the idea and apply one useful step.",
        max_length=240,
    )
    visual_direction: str = Field(
        default="Premium founder-led editorial treatment with evidence on screen.",
        max_length=2000,
    )
    production_constraints: list[str] = Field(default_factory=list, max_length=20)
    duration_seconds: int = Field(default=60, ge=15, le=3600)
    cta: str = Field(default="What system are you building next?", max_length=500)
    success_metric: str = Field(default="Qualified saves and substantive replies", max_length=240)


class ContentBriefView(ORMModel):
    id: str
    idea_id: str
    content_item_id: str
    title: str
    objective: str
    audience: str
    platform: str
    format: str
    pillar: str
    series: str | None
    core_message: str
    audience_problem: str
    desired_emotion: str
    desired_action: str
    proof_points: list[dict[str, Any]]
    benchmark_references: list[dict[str, Any]]
    visual_direction: str
    production_constraints: list[str]
    duration_seconds: int
    cta: str
    success_metric: str
    evidence_status: ReviewStatus
    status: BriefStatus
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class ScriptVersionCreate(BaseModel):
    body_text: str = Field(min_length=20, max_length=100_000)
    hook_selected: str = Field(min_length=3, max_length=500)
    hook_variants: list[str] = Field(default_factory=list, max_length=20)
    on_screen_text: list[str] = Field(default_factory=list, max_length=50)
    b_roll_notes: list[str] = Field(default_factory=list, max_length=50)
    camera_notes: list[str] = Field(default_factory=list, max_length=50)
    cta: str = Field(min_length=2, max_length=500)
    duration_seconds: int = Field(ge=10, le=7200)
    brand_alignment_score: float = Field(default=0, ge=0, le=10)
    originality_score: float = Field(default=0, ge=0, le=10)
    evidence_notes: list[str] = Field(default_factory=list, max_length=50)
    change_summary: str = Field(default="Initial script draft", min_length=3, max_length=500)

    @field_validator("hook_variants")
    @classmethod
    def unique_hooks(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in value if item.strip()))


class HookOptionView(ORMModel):
    id: str
    script_version_id: str
    text: str
    category: str
    clarity_score: float
    curiosity_score: float
    specificity_score: float
    brand_fit_score: float
    audience_fit_score: float
    originality_score: float
    total_score: float
    is_recommended: bool
    fatigue_warning: str | None


class ScriptVersionView(ORMModel):
    id: str
    script_id: str
    version_number: int
    body_text: str
    hook_selected: str
    on_screen_text: list[str]
    b_roll_notes: list[str]
    camera_notes: list[str]
    cta: str
    duration_seconds: int
    brand_alignment_score: float
    originality_score: float
    evidence_notes: list[str]
    change_summary: str
    checksum_sha256: str
    created_by: str
    approval_id: str | None
    is_active: bool
    created_at: datetime


class FactCheckCreate(BaseModel):
    claim_table: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    sources: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    unresolved_claims: list[str] = Field(default_factory=list, max_length=100)
    verified_text: str = Field(min_length=20, max_length=100_000)
    confidence: float = Field(ge=0, le=1)


class FactCheckView(ORMModel):
    id: str
    script_version_id: str
    status: ReviewStatus
    claim_table: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    unresolved_claims: list[str]
    verified_text: str
    confidence: float
    financial_classification: str
    blocked_claims: list[str]
    risk_disclosures: list[str]
    reviewed_by: str
    reviewed_at: datetime


class ScriptView(ORMModel):
    id: str
    content_brief_id: str
    content_item_id: str
    title: str
    status: ScriptStatus
    current_version_id: str | None
    version_count: int
    fact_check_status: ReviewStatus
    financial_risk: RiskLevel
    approval_status: ApprovalStatus
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    current_version: ScriptVersionView | None = None
    hooks: list[HookOptionView] = Field(default_factory=list)
    fact_check: FactCheckView | None = None


class ScriptApprovalResult(BaseModel):
    script: ScriptView
    approval_id: str


class CapacityPlanCreate(BaseModel):
    week_start: date
    available_hours: float = Field(default=10, ge=1, le=168)
    max_shoots: int = Field(default=2, ge=0, le=50)
    max_edits: int = Field(default=3, ge=0, le=50)
    fallback_plan: str = Field(
        default="Publish one low-production proof note if the planned shoot slips.",
        min_length=10,
        max_length=2000,
    )
    notes: str | None = Field(default=None, max_length=2000)


class CapacityPlanView(ORMModel):
    id: str
    week_start: date
    available_hours: float
    max_shoots: int
    max_edits: int
    fallback_plan: str
    notes: str | None
    is_demo: bool


class CalendarEventCreate(BaseModel):
    content_item_id: str | None = None
    title: str = Field(min_length=3, max_length=240)
    event_type: str = Field(pattern="^(research|write|review|shoot|edit|editorial_publish)$")
    start_at: datetime
    end_at: datetime
    timezone: str = Field(default="America/Toronto", max_length=80)
    capacity_units: float = Field(default=1, gt=0, le=24)
    notes: str | None = Field(default=None, max_length=2000)


class CalendarEventView(ORMModel):
    id: str
    content_item_id: str | None
    title: str
    event_type: str
    start_at: datetime
    end_at: datetime
    timezone: str
    status: str
    capacity_units: float
    notes: str | None
    is_demo: bool
    created_at: datetime


class ProductionPlanUpdate(BaseModel):
    location: str | None = Field(default=None, max_length=240)
    scheduled_at: datetime | None = None
    equipment: list[str] | None = Field(default=None, max_length=50)
    wardrobe: list[str] | None = Field(default=None, max_length=50)
    props: list[str] | None = Field(default=None, max_length=50)
    estimated_minutes: int | None = Field(default=None, ge=10, le=1440)


class ProductionSceneView(ORMModel):
    id: str
    sequence: int
    title: str
    purpose: str
    dialogue: str
    duration_seconds: int


class ProductionShotView(ORMModel):
    id: str
    production_scene_id: str
    sequence: int
    framing: str
    camera_angle: str
    movement: str
    lighting: str
    instructions: str
    is_b_roll: bool
    status: str


class ChecklistItemView(ORMModel):
    id: str
    phase: str
    label: str
    is_critical: bool
    is_complete: bool
    completed_at: datetime | None


class ChecklistToggle(BaseModel):
    is_complete: bool


class ProductionPlanView(ORMModel):
    id: str
    content_item_id: str
    script_id: str
    title: str
    creative_treatment: str
    location: str | None
    equipment: list[str]
    wardrobe: list[str]
    props: list[str]
    lighting_plan: str
    music_direction: str
    scheduled_at: datetime | None
    estimated_minutes: int
    status: ProductionStatus
    readiness_score: float
    blockers: list[str]
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    scenes: list[ProductionSceneView] = Field(default_factory=list)
    shots: list[ProductionShotView] = Field(default_factory=list)
    checklist: list[ChecklistItemView] = Field(default_factory=list)


class AssetView(ORMModel):
    id: str
    content_item_id: str | None
    production_plan_id: str | None
    filename: str
    storage_key: str
    media_type: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    tags: list[str]
    people: list[str]
    location: str | None
    orientation: str | None
    quality_score: float
    rights_status: RightsStatus
    rights_notes: str | None
    original_preserved: bool
    duplicate_of_id: str | None
    is_demo: bool
    created_at: datetime


class ProofItemCreate(BaseModel):
    content_item_id: str | None = None
    title: str = Field(min_length=3, max_length=240)
    proof_type: str = Field(default="build_log", max_length=80)
    credibility_gap: str = Field(min_length=3, max_length=5000)
    context: str = Field(min_length=3, max_length=20_000)
    constraints: str = Field(min_length=3, max_length=20_000)
    process: str = Field(min_length=3, max_length=20_000)
    output: str = Field(min_length=3, max_length=20_000)
    result: str = Field(min_length=3, max_length=20_000)
    lessons: str = Field(min_length=3, max_length=20_000)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    asset_ids: list[str] = Field(default_factory=list, max_length=100)
    permission_status: str = Field(default="not_required", max_length=60)
    sensitivity: str = Field(default="internal", max_length=60)


class ProofItemView(ORMModel):
    id: str
    content_item_id: str | None
    title: str
    proof_type: str
    credibility_gap: str
    context: str
    constraints: str
    process: str
    output: str
    result: str
    lessons: str
    evidence_links: list[dict[str, Any]]
    asset_ids: list[str]
    permission_status: str
    sensitivity: str
    status: ProofStatus
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class MemoryRecordCreate(BaseModel):
    memory_type: str = Field(default="working_note", min_length=3, max_length=80)
    title: str = Field(min_length=3, max_length=240)
    content: str = Field(min_length=3, max_length=200_000)
    vault_path: str = Field(min_length=3, max_length=800)
    confidence: float = Field(default=0.5, ge=0, le=1)
    sensitivity: str = Field(default="internal", max_length=60)


class MemoryRecordView(ORMModel):
    id: str
    memory_type: str
    title: str
    content: str
    canonical_status: CanonicalStatus
    confidence: float
    provenance: dict[str, Any]
    vault_path: str
    content_checksum: str
    sensitivity: str
    review_at: datetime | None
    sync_status: str
    embedding_status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class SyncEventView(ORMModel):
    id: str
    direction: str
    record_type: str
    record_id: str | None
    vault_path: str
    status: str
    database_checksum: str | None
    vault_checksum: str | None
    details: dict[str, Any]
    created_at: datetime


class VaultSyncResult(BaseModel):
    root: str
    initialized_folders: int
    exported: int
    imported: int
    conflicts: int
    skipped: int
    events: list[SyncEventView] = Field(default_factory=list)


class MemorySearchResult(BaseModel):
    id: str
    record_type: str
    title: str
    excerpt: str
    authority: str
    source_path: str | None
    score: float
    confidence: float
    is_demo: bool


class CreatorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    username: str = Field(min_length=2, max_length=180)
    platform: str = Field(min_length=2, max_length=60)
    url: str = Field(min_length=8, max_length=800)
    category: str = Field(default="Builder Intelligence", max_length=120)
    why_tracked: str = Field(min_length=3, max_length=5000)
    tier: int = Field(default=3, ge=1, le=4)
    relevance_score: float = Field(default=7, ge=0, le=10)
    content_pillars: list[str] = Field(default_factory=list, max_length=20)
    formats: list[str] = Field(default_factory=list, max_length=20)
    voice: str = Field(default="Not yet analyzed", max_length=5000)
    hook_style: str = Field(default="Not yet analyzed", max_length=5000)
    production_style: str = Field(default="Not yet analyzed", max_length=5000)
    audience: str = Field(default="Builders and operators", max_length=240)


class CreatorView(ORMModel):
    id: str
    name: str
    username: str
    platform: str
    url: str
    category: str
    why_tracked: str
    tier: int
    relevance_score: float
    content_pillars: list[str]
    formats: list[str]
    voice: str
    hook_style: str
    production_style: str
    audience: str
    last_reviewed_at: datetime | None
    watch_status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class BenchmarkCreate(BaseModel):
    creator_id: str | None = None
    source_url: str = Field(min_length=8, max_length=1200)
    title: str = Field(min_length=3, max_length=240)
    transcript_excerpt: str | None = Field(default=None, max_length=5000)
    observed_hook: str = Field(min_length=3, max_length=5000)
    observed_structure: str = Field(min_length=3, max_length=5000)
    visual_notes: str = Field(default="Visual evidence was not supplied.", max_length=5000)
    editing_notes: str = Field(default="Editing evidence was not supplied.", max_length=5000)
    transferable_mechanics: list[str] = Field(min_length=1, max_length=20)
    pattern_tags: list[str] = Field(default_factory=list, max_length=30)


class BenchmarkView(ORMModel):
    id: str
    creator_id: str | None
    source_url: str
    platform: str
    title: str
    source_type: str
    raw_metadata: dict[str, Any]
    transcript_excerpt: str | None
    hook_analysis: str
    structure_analysis: str
    visual_analysis: str
    editing_analysis: str
    transferable_mechanics: list[str]
    protected_identity: list[str]
    mezie_adaptations: list[str]
    pattern_tags: list[str]
    limitations: list[str]
    evidence_level: str
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class TelegramCapture(BaseModel):
    sender_id: int
    message_type: str = Field(pattern="^(text|voice|link)$")
    text: str | None = Field(default=None, max_length=20_000)
    transcript: str | None = Field(default=None, max_length=20_000)
    source_reference: str | None = Field(default=None, max_length=800)


class TelegramMessageView(ORMModel):
    id: str
    update_id: str
    sender_id: str
    message_id: str | None
    message_type: str
    text: str | None
    transcript: str | None
    source_reference: str | None
    classification: str
    status: str
    created_record_type: str | None
    created_record_id: str | None
    response_text: str
    failure_reason: str | None
    is_demo: bool
    created_at: datetime


class HeartbeatRunRequest(BaseModel):
    run_date: date | None = None
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=160)


class DailyBriefView(ORMModel):
    id: str
    heartbeat_run_id: str
    brief_date: date
    title: str
    what_changed: list[dict[str, Any]]
    creator_watch: list[dict[str, Any]]
    trend_signals: list[dict[str, Any]]
    content_opportunities: list[dict[str, Any]]
    risks_noise: list[str]
    recommended_actions: list[str]
    recommended_action: str
    coverage_gaps: list[str]
    vault_path: str | None
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class HeartbeatRunView(ORMModel):
    id: str
    run_date: date
    trigger: str
    idempotency_key: str
    status: str
    source_coverage: list[dict[str, Any]]
    model_alias: str
    tools_used: list[str]
    model_cost: float
    tool_cost: float
    context_pack_id: str | None
    records_changed: list[dict[str, Any]]
    errors: list[str]
    confidence: float
    completed_at: datetime | None
    is_demo: bool
    created_at: datetime
    brief: DailyBriefView | None = None


class HeartbeatSettingUpdate(BaseModel):
    enabled: bool | None = None
    schedule_hour: int | None = Field(default=None, ge=0, le=23)
    timezone: str | None = Field(default=None, min_length=3, max_length=80)
    mode: str | None = Field(default=None, pattern="^(lean|standard|deep)$")
    max_sources: int | None = Field(default=None, ge=1, le=100)
    max_creators: int | None = Field(default=None, ge=1, le=50)
    telegram_summary_enabled: bool | None = None


class HeartbeatSettingView(ORMModel):
    id: str
    enabled: bool
    schedule_hour: int
    timezone: str
    mode: str
    max_sources: int
    max_creators: int
    telegram_summary_enabled: bool
    updated_at: datetime


class MetricCreate(BaseModel):
    content_item_id: str | None = None
    platform: str = Field(min_length=2, max_length=60)
    captured_at: datetime | None = None
    views: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    engagement: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    watch_time_seconds: float = Field(default=0, ge=0)


class MetricSnapshotView(ORMModel):
    id: str
    content_item_id: str | None
    platform: str
    captured_at: datetime
    views: int
    impressions: int
    engagement: int
    saves: int
    shares: int
    watch_time_seconds: float
    is_demo: bool
    created_at: datetime


class InsightView(ORMModel):
    id: str
    content_item_id: str | None
    classification: str
    title: str
    observation: str
    hypothesis: str
    evidence: list[dict[str, Any]]
    confidence: float
    status: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class AnalyticsOverview(BaseModel):
    metrics: list[MetricSnapshotView]
    insights: list[InsightView]
    totals: dict[str, float]
    platform_breakdown: list[dict[str, Any]]


class AnalyticsImportResult(BaseModel):
    imported: int
    rejected: int
    errors: list[str]
    insight_ids: list[str]


class ExperimentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    question: str = Field(min_length=3, max_length=5000)
    hypothesis: str = Field(min_length=3, max_length=5000)
    variable: str = Field(min_length=2, max_length=240)
    control_conditions: list[str] = Field(min_length=1, max_length=20)
    platform: str = Field(min_length=2, max_length=60)
    content_type: str = Field(min_length=2, max_length=80)
    expected_outcome: str = Field(min_length=3, max_length=5000)
    success_metric: str = Field(min_length=2, max_length=240)
    measurement_start: date | None = None
    measurement_end: date | None = None


class ExperimentView(ORMModel):
    id: str
    title: str
    question: str
    hypothesis: str
    variable: str
    control_conditions: list[str]
    platform: str
    content_type: str
    expected_outcome: str
    success_metric: str
    measurement_start: date | None
    measurement_end: date | None
    status: str
    result: str | None
    interpretation: str | None
    confidence: float
    decision: str | None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
