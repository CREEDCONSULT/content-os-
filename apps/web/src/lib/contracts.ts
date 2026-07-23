export type AuthUser = {
  username: string;
  display_name: string;
  permissions: string[];
};

export type DashboardMetric = {
  label: string;
  value: number | string;
  delta: string | null;
  accent: "blue" | "gold" | "green" | "purple" | string;
  is_demo: boolean;
};

export type DashboardSummary = {
  greeting_name: string;
  brand_name: string;
  signature_line: string;
  metrics: DashboardMetric[];
  pipeline_groups: Record<PipelineGroup, number>;
  today: {
    id: string;
    title: string;
    due_at: string | null;
    priority: string;
    status: string;
  }[];
  recent_activity: {
    id: string;
    event_type: string;
    summary: string;
    created_at: string;
    is_demo: boolean;
  }[];
  upcoming_content: {
    id: string;
    title: string;
    platform: string;
    due_date: string | null;
    status: PipelineStatus;
  }[];
  pending_approvals: number;
  agent: {
    status: string;
    model_alias: string;
    current_focus: string;
    last_run_at: string | null;
    is_mock: boolean;
  };
};

export type CanonicalStatus = "canonical" | "working" | "archived" | "restricted";

export type BrandDocument = {
  id: string;
  document_type: string;
  title: string;
  slug: string;
  canonical_status: CanonicalStatus;
  source_path: string | null;
  vault_path: string | null;
  sensitivity: string;
  tags: string[];
  version_count: number;
  updated_at: string;
};

export type BrandDocumentDetail = BrandDocument & {
  current_version: {
    id: string;
    version_number: number;
    content_markdown: string;
    change_summary: string;
    checksum_sha256: string;
    provenance: Record<string, unknown>;
    created_by: string;
    approval_id: string | null;
    is_active: boolean;
    created_at: string;
  } | null;
};

export type IdeaStatus =
  | "captured"
  | "clarifying"
  | "researching"
  | "selected"
  | "rejected"
  | "converted_to_brief"
  | "archived";

export type Idea = {
  id: string;
  title: string;
  raw_input: string;
  source_type: string;
  source_reference: string | null;
  pillar: string | null;
  series: string | null;
  audience: string;
  platform_fit: string[];
  strategic_objective: string | null;
  urgency: string;
  status: IdeaStatus;
  brand_fit_score: number;
  audience_value_score: number;
  proof_score: number;
  timeliness_score: number;
  originality_score: number;
  feasibility_score: number;
  strategic_importance_score: number;
  total_priority_score: number;
  rejection_reason: string | null;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type IdeaList = {
  items: Idea[];
  total: number;
};

export type PipelineStatus =
  | "idea"
  | "research"
  | "brief"
  | "script"
  | "review"
  | "approved"
  | "ready_to_shoot"
  | "shot"
  | "editing"
  | "review_edit"
  | "ready_to_publish"
  | "published"
  | "analytics_review"
  | "repurpose"
  | "archived";

export type PipelineGroup =
  | "ideation"
  | "scripting"
  | "production"
  | "review"
  | "published";

export type ContentItem = {
  id: string;
  idea_id: string | null;
  title: string;
  platform: string;
  format: string;
  pillar: string;
  series: string | null;
  audience: string;
  objective: string;
  status: PipelineStatus;
  priority: string;
  due_date: string | null;
  publish_at: string | null;
  readiness_score: number;
  approval_status: "not_required" | "pending" | "approved" | "rejected";
  blocker: string | null;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type ContentList = {
  items: ContentItem[];
  total: number;
  groups: Record<PipelineGroup, number>;
};

export type Approval = {
  id: string;
  action_type: string;
  target_type: string;
  target_id: string;
  requested_by: string;
  risk_level: "low" | "medium" | "high" | "critical";
  cost_estimate: number;
  status: "pending" | "approved" | "rejected";
  context: Record<string, unknown>;
  approved_by: string | null;
  decided_at: string | null;
  notes: string | null;
  created_at: string;
};

export type Integration = {
  id: string;
  label: string;
  state: "configured" | "mock" | "disabled" | "error";
  detail: string;
  last_checked_at: string;
  server_side_only: boolean;
};

export type SkillDefinition = {
  id: string;
  slug: string;
  name: string;
  version: string;
  description: string;
  trigger_summary: string;
  input_schema: Record<string, unknown>;
  required_context: string[];
  allowed_tools: string[];
  workflow: string[];
  output_schema: Record<string, unknown>;
  memory_policy: string;
  approval_policy: string;
  failure_behavior: string;
  model_profile: string;
  timeout_seconds: number;
  cost_class: string;
  source_path: string;
  enabled: boolean;
};

export type ContextSource = {
  document_id: string;
  version_id: string;
  title: string;
  source_path: string | null;
  classification: string;
  authority: string;
  checksum_sha256: string;
  pack_fingerprint?: string;
};

export type AgentRun = {
  id: string;
  request_id: string;
  idempotency_key: string | null;
  channel: string;
  intent: string;
  status: "running" | "completed" | "blocked" | "failed";
  provider: "mock" | "openai" | string;
  model_alias: string;
  context_pack_id: string | null;
  skills_used: string[];
  tools_used: string[];
  context_loaded: ContextSource[];
  input_envelope: Record<string, unknown>;
  output_envelope: {
    skill?: string;
    status?: string;
    summary?: string;
    outputs?: {
      provider_output?: {
        summary?: string;
        classifications?: {
          statement: string;
          type: string;
          evidence: string;
        }[];
        warnings?: string[];
        next_actions?: string[];
        confidence?: number;
      };
      [key: string]: unknown;
    };
    warnings?: string[];
    next_actions?: string[];
    [key: string]: unknown;
  };
  model_cost: number;
  tool_cost: number;
  confidence: number;
  summary: string;
  proposed_writes: Record<string, unknown>[];
  completed_writes: Record<string, unknown>[];
  approvals_required: {
    approval_id: string;
    action_type: string;
    risk_level: string;
  }[];
  next_actions: string[];
  error: string | null;
  completed_at: string | null;
  is_demo: boolean;
  created_at: string;
};

export type AgentRunList = {
  items: AgentRun[];
  total: number;
};

export type ContentBrief = {
  id: string;
  idea_id: string;
  content_item_id: string;
  title: string;
  objective: string;
  audience: string;
  platform: string;
  format: string;
  pillar: string;
  series: string | null;
  core_message: string;
  audience_problem: string;
  desired_emotion: string;
  desired_action: string;
  proof_points: Record<string, unknown>[];
  benchmark_references: Record<string, unknown>[];
  visual_direction: string;
  production_constraints: string[];
  duration_seconds: number;
  cta: string;
  success_metric: string;
  evidence_status: "not_started" | "needs_review" | "verified" | "blocked";
  status: "draft" | "proof_needed" | "ready" | "archived";
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type ScriptVersion = {
  id: string;
  script_id: string;
  version_number: number;
  body_text: string;
  hook_selected: string;
  on_screen_text: string[];
  b_roll_notes: string[];
  camera_notes: string[];
  cta: string;
  duration_seconds: number;
  brand_alignment_score: number;
  originality_score: number;
  evidence_notes: string[];
  change_summary: string;
  checksum_sha256: string;
  created_by: string;
  approval_id: string | null;
  is_active: boolean;
  created_at: string;
};

export type HookOption = {
  id: string;
  script_version_id: string;
  text: string;
  category: string;
  clarity_score: number;
  curiosity_score: number;
  specificity_score: number;
  brand_fit_score: number;
  audience_fit_score: number;
  originality_score: number;
  total_score: number;
  is_recommended: boolean;
  fatigue_warning: string | null;
};

export type FactCheck = {
  id: string;
  script_version_id: string;
  status: "not_started" | "needs_review" | "verified" | "blocked";
  claim_table: Record<string, unknown>[];
  sources: Record<string, unknown>[];
  unresolved_claims: string[];
  verified_text: string;
  confidence: number;
  financial_classification: string;
  blocked_claims: string[];
  risk_disclosures: string[];
  reviewed_by: string;
  reviewed_at: string;
};

export type Script = {
  id: string;
  content_brief_id: string;
  content_item_id: string;
  title: string;
  status: "draft" | "review" | "approved" | "rejected" | "archived";
  current_version_id: string | null;
  version_count: number;
  fact_check_status: "not_started" | "needs_review" | "verified" | "blocked";
  financial_risk: "low" | "medium" | "high" | "critical";
  approval_status: "not_required" | "pending" | "approved" | "rejected";
  is_demo: boolean;
  created_at: string;
  updated_at: string;
  current_version: ScriptVersion | null;
  hooks: HookOption[];
  fact_check: FactCheck | null;
};

export type CapacityPlan = {
  id: string;
  week_start: string;
  available_hours: number;
  max_shoots: number;
  max_edits: number;
  fallback_plan: string;
  notes: string | null;
  is_demo: boolean;
};

export type CalendarEvent = {
  id: string;
  content_item_id: string | null;
  title: string;
  event_type: "research" | "write" | "review" | "shoot" | "edit" | "editorial_publish";
  start_at: string;
  end_at: string;
  timezone: string;
  status: string;
  capacity_units: number;
  notes: string | null;
  is_demo: boolean;
  created_at: string;
};

export type ProductionScene = {
  id: string;
  sequence: number;
  title: string;
  purpose: string;
  dialogue: string;
  duration_seconds: number;
};

export type ProductionShot = {
  id: string;
  production_scene_id: string;
  sequence: number;
  framing: string;
  camera_angle: string;
  movement: string;
  lighting: string;
  instructions: string;
  is_b_roll: boolean;
  status: string;
};

export type ChecklistItem = {
  id: string;
  phase: string;
  label: string;
  is_critical: boolean;
  is_complete: boolean;
  completed_at: string | null;
};

export type ProductionPlan = {
  id: string;
  content_item_id: string;
  script_id: string;
  title: string;
  creative_treatment: string;
  location: string | null;
  equipment: string[];
  wardrobe: string[];
  props: string[];
  lighting_plan: string;
  music_direction: string;
  scheduled_at: string | null;
  estimated_minutes: number;
  status: "draft" | "blocked" | "ready" | "in_progress" | "complete";
  readiness_score: number;
  blockers: string[];
  is_demo: boolean;
  created_at: string;
  updated_at: string;
  scenes: ProductionScene[];
  shots: ProductionShot[];
  checklist: ChecklistItem[];
};

export type Asset = {
  id: string;
  content_item_id: string | null;
  production_plan_id: string | null;
  filename: string;
  storage_key: string;
  media_type: string;
  mime_type: string;
  size_bytes: number;
  checksum_sha256: string;
  tags: string[];
  people: string[];
  location: string | null;
  orientation: string | null;
  quality_score: number;
  rights_status: "unknown" | "owned" | "licensed" | "restricted";
  rights_notes: string | null;
  original_preserved: boolean;
  duplicate_of_id: string | null;
  is_demo: boolean;
  created_at: string;
};

export type ProofItem = {
  id: string;
  content_item_id: string | null;
  title: string;
  proof_type: string;
  credibility_gap: string;
  context: string;
  constraints: string;
  process: string;
  output: string;
  result: string;
  lessons: string;
  evidence_links: { label?: string; url?: string; [key: string]: unknown }[];
  asset_ids: string[];
  permission_status: string;
  sensitivity: string;
  status: "draft" | "evidence_needed" | "verified" | "approved" | "archived";
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type MemoryRecord = {
  id: string;
  memory_type: string;
  title: string;
  content: string;
  canonical_status: CanonicalStatus;
  confidence: number;
  provenance: Record<string, unknown>;
  vault_path: string;
  content_checksum: string;
  sensitivity: string;
  review_at: string | null;
  sync_status: string;
  embedding_status: string;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type VaultSyncResult = {
  root: string;
  initialized_folders: number;
  exported: number;
  imported: number;
  conflicts: number;
  skipped: number;
  events: {
    id: string;
    direction: string;
    record_type: string;
    record_id: string | null;
    vault_path: string;
    status: string;
    details: Record<string, unknown>;
    created_at: string;
  }[];
};

export type Creator = {
  id: string;
  name: string;
  username: string;
  platform: string;
  url: string;
  category: string;
  why_tracked: string;
  tier: number;
  relevance_score: number;
  content_pillars: string[];
  formats: string[];
  voice: string;
  hook_style: string;
  production_style: string;
  audience: string;
  last_reviewed_at: string | null;
  watch_status: string;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type Benchmark = {
  id: string;
  creator_id: string | null;
  source_url: string;
  platform: string;
  title: string;
  source_type: string;
  raw_metadata: Record<string, unknown>;
  transcript_excerpt: string | null;
  hook_analysis: string;
  structure_analysis: string;
  visual_analysis: string;
  editing_analysis: string;
  transferable_mechanics: string[];
  protected_identity: string[];
  mezie_adaptations: string[];
  pattern_tags: string[];
  limitations: string[];
  evidence_level: string;
  status: string;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type TelegramMessage = {
  id: string;
  update_id: string;
  sender_id: string;
  message_id: string | null;
  message_type: string;
  text: string | null;
  transcript: string | null;
  source_reference: string | null;
  classification: string;
  status: string;
  created_record_type: string | null;
  created_record_id: string | null;
  response_text: string;
  failure_reason: string | null;
  is_demo: boolean;
  created_at: string;
};

export type DailyBrief = {
  id: string;
  heartbeat_run_id: string;
  brief_date: string;
  title: string;
  what_changed: Record<string, unknown>[];
  creator_watch: Record<string, unknown>[];
  trend_signals: Record<string, unknown>[];
  content_opportunities: Record<string, unknown>[];
  risks_noise: string[];
  recommended_actions: string[];
  recommended_action: string;
  coverage_gaps: string[];
  vault_path: string | null;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type HeartbeatRun = {
  id: string;
  run_date: string;
  trigger: string;
  idempotency_key: string;
  status: string;
  source_coverage: Record<string, unknown>[];
  model_alias: string;
  tools_used: string[];
  model_cost: number;
  tool_cost: number;
  context_pack_id: string | null;
  records_changed: Record<string, unknown>[];
  errors: string[];
  confidence: number;
  completed_at: string | null;
  is_demo: boolean;
  created_at: string;
  brief: DailyBrief | null;
};

export type MetricSnapshot = {
  id: string;
  content_item_id: string | null;
  platform: string;
  captured_at: string;
  views: number;
  impressions: number;
  engagement: number;
  saves: number;
  shares: number;
  watch_time_seconds: number;
  is_demo: boolean;
  created_at: string;
};

export type Insight = {
  id: string;
  content_item_id: string | null;
  classification: string;
  title: string;
  observation: string;
  hypothesis: string;
  evidence: Record<string, unknown>[];
  confidence: number;
  status: string;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type AnalyticsOverview = {
  metrics: MetricSnapshot[];
  insights: Insight[];
  totals: Record<"views" | "impressions" | "engagement" | "saves" | "shares", number>;
  platform_breakdown: {
    platform: string;
    views: number;
    engagement: number;
    saves: number;
    shares: number;
    records: number;
  }[];
};

export type Experiment = {
  id: string;
  title: string;
  question: string;
  hypothesis: string;
  variable: string;
  control_conditions: string[];
  platform: string;
  content_type: string;
  expected_outcome: string;
  success_metric: string;
  measurement_start: string | null;
  measurement_end: string | null;
  status: string;
  result: string | null;
  interpretation: string | null;
  confidence: number;
  decision: string | null;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
};

export type GlobalSearchResult = {
  id: string;
  record_type:
    | "brand_document"
    | "idea"
    | "content_item"
    | "memory"
    | "creator"
    | "benchmark";
  title: string;
  excerpt: string;
  href: string;
  authority: string;
  score: number;
  is_demo: boolean;
};
