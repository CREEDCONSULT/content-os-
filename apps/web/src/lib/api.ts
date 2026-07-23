import type {
  AgentRun,
  AgentRunList,
  Approval,
  Asset,
  AnalyticsOverview,
  AuthUser,
  BrandDocument,
  BrandDocumentDetail,
  CalendarEvent,
  CapacityPlan,
  Benchmark,
  Creator,
  ContentItem,
  ContentBrief,
  ContentList,
  DashboardSummary,
  Experiment,
  GlobalSearchResult,
  HeartbeatRun,
  Idea,
  IdeaList,
  Integration,
  MemoryRecord,
  PipelineStatus,
  ProductionPlan,
  ProofItem,
  SkillDefinition,
  Script,
  TelegramMessage,
  VaultSyncResult,
} from "@/lib/contracts";
import {
  type CreateIdeaPayload,
  queueOfflineIdea,
} from "@/lib/offline-ideas";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // Keep the status-based fallback when a server does not return JSON.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  login: (username: string, password: string) =>
    request<{ user: AuthUser; expires_in: number }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  me: () => request<AuthUser>("/api/v1/auth/me"),
  logout: () => request<void>("/api/v1/auth/logout", { method: "POST" }),
  dashboard: () => request<DashboardSummary>("/api/v1/dashboard/summary"),
  brandDocuments: (search = "") =>
    request<BrandDocument[]>(
      `/api/v1/brand/documents${search ? `?search=${encodeURIComponent(search)}` : ""}`,
    ),
  brandDocument: (id: string) =>
    request<BrandDocumentDetail>(`/api/v1/brand/documents/${id}`),
  ideas: (search = "", status = "") => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    const suffix = params.size ? `?${params}` : "";
    return request<IdeaList>(`/api/v1/ideas${suffix}`);
  },
  createIdea: (payload: CreateIdeaPayload) =>
    request<Idea>("/api/v1/ideas", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createIdeaOrQueue: async (
    payload: CreateIdeaPayload,
  ): Promise<
    | { mode: "created"; idea: Idea }
    | { mode: "queued"; queue_id: string }
  > => {
    try {
      return { mode: "created", idea: await api.createIdea(payload) };
    } catch (error) {
      if (error instanceof ApiError) throw error;
      const queued = queueOfflineIdea(payload);
      return { mode: "queued", queue_id: queued.id };
    }
  },
  content: () => request<ContentList>("/api/v1/content"),
  transitionContent: (id: string, toStatus: PipelineStatus) =>
    request<ContentItem>(`/api/v1/content/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_status: toStatus }),
    }),
  approvals: (status = "pending") =>
    request<Approval[]>(`/api/v1/approvals?status=${encodeURIComponent(status)}`),
  decideApproval: (id: string, decision: "approved" | "rejected", notes?: string) =>
    request<Approval>(`/api/v1/approvals/${id}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, notes }),
    }),
  integrations: () =>
    request<{ items: Integration[] }>("/api/v1/integrations/status"),
  skills: () => request<SkillDefinition[]>("/api/v1/agent/skills"),
  agentRuns: () => request<AgentRunList>("/api/v1/agent/runs"),
  createAgentRun: (payload: {
    intent: string;
    idempotency_key: string;
    budget: { model_usd: number; tool_usd: number };
    raw_input?: Record<string, unknown>;
  }) =>
    request<AgentRun>("/api/v1/agent/runs", {
      method: "POST",
      body: JSON.stringify({ channel: "dashboard", ...payload }),
    }),
  briefs: () => request<ContentBrief[]>("/api/v1/studio/briefs"),
  createBriefFromIdea: (
    ideaId: string,
    payload: { platform: string; format: string },
  ) =>
    request<ContentBrief>(`/api/v1/studio/briefs/from-idea/${ideaId}`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  scripts: () => request<Script[]>("/api/v1/studio/scripts"),
  createScript: (
    briefId: string,
    payload: {
      body_text: string;
      hook_selected: string;
      hook_variants: string[];
      cta: string;
      duration_seconds: number;
      brand_alignment_score: number;
      originality_score: number;
      change_summary: string;
    },
  ) =>
    request<Script>(`/api/v1/studio/briefs/${briefId}/scripts`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  addScriptVersion: (
    scriptId: string,
    payload: {
      body_text: string;
      hook_selected: string;
      hook_variants: string[];
      cta: string;
      duration_seconds: number;
      brand_alignment_score: number;
      originality_score: number;
      change_summary: string;
    },
  ) =>
    request<Script>(`/api/v1/studio/scripts/${scriptId}/versions`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  factCheckScript: (
    scriptId: string,
    payload: {
      claim_table: Record<string, unknown>[];
      sources: Record<string, unknown>[];
      unresolved_claims: string[];
      verified_text: string;
      confidence: number;
    },
  ) =>
    request<Script["fact_check"]>(`/api/v1/studio/scripts/${scriptId}/fact-check`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  submitScript: (scriptId: string) =>
    request<{ script: Script; approval_id: string }>(
      `/api/v1/studio/scripts/${scriptId}/submit`,
      { method: "POST" },
    ),
  capacities: () => request<CapacityPlan[]>("/api/v1/calendar/capacity"),
  setCapacity: (payload: {
    week_start: string;
    available_hours: number;
    max_shoots: number;
    max_edits: number;
    fallback_plan: string;
    notes?: string;
  }) =>
    request<CapacityPlan>("/api/v1/calendar/capacity", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  calendarEvents: () => request<CalendarEvent[]>("/api/v1/calendar/events"),
  createCalendarEvent: (payload: {
    title: string;
    event_type: CalendarEvent["event_type"];
    start_at: string;
    end_at: string;
    capacity_units: number;
    notes?: string;
  }) =>
    request<CalendarEvent>("/api/v1/calendar/events", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  productionPlans: () => request<ProductionPlan[]>("/api/v1/production/plans"),
  createProductionPlan: (scriptId: string) =>
    request<ProductionPlan>(`/api/v1/production/plans/from-script/${scriptId}`, {
      method: "POST",
    }),
  updateProductionPlan: (
    planId: string,
    payload: {
      location?: string;
      scheduled_at?: string;
      equipment?: string[];
      wardrobe?: string[];
      props?: string[];
      estimated_minutes?: number;
    },
  ) =>
    request<ProductionPlan>(`/api/v1/production/plans/${planId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  setChecklistItem: (itemId: string, isComplete: boolean) =>
    request<ProductionPlan>(`/api/v1/production/checklist/${itemId}`, {
      method: "POST",
      body: JSON.stringify({ is_complete: isComplete }),
    }),
  assets: () => request<Asset[]>("/api/v1/assets"),
  uploadAsset: async (formData: FormData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/assets`, {
      method: "POST",
      credentials: "include",
      body: formData,
    });
    if (!response.ok) {
      let message = `Upload failed (${response.status})`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) message = body.detail;
      } catch {
        // Retain the status fallback for non-JSON errors.
      }
      throw new ApiError(message, response.status);
    }
    return (await response.json()) as Asset;
  },
  proofItems: () => request<ProofItem[]>("/api/v1/proof"),
  createProofItem: (payload: {
    title: string;
    proof_type: string;
    credibility_gap: string;
    context: string;
    constraints: string;
    process: string;
    output: string;
    result: string;
    lessons: string;
    evidence_links: { label: string; url: string }[];
    permission_status: string;
    sensitivity: string;
  }) =>
    request<ProofItem>("/api/v1/proof", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  memoryRecords: () => request<MemoryRecord[]>("/api/v1/memory/records"),
  syncVault: () =>
    request<VaultSyncResult>("/api/v1/memory/vault/sync", { method: "POST" }),
  creators: () => request<Creator[]>("/api/v1/intelligence/creators"),
  createCreator: (payload: {
    name: string;
    username: string;
    platform: string;
    url: string;
    why_tracked: string;
    tier: number;
    relevance_score: number;
  }) =>
    request<Creator>("/api/v1/intelligence/creators", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  benchmarks: () => request<Benchmark[]>("/api/v1/intelligence/benchmarks"),
  createBenchmark: (payload: {
    creator_id?: string;
    source_url: string;
    title: string;
    transcript_excerpt?: string;
    observed_hook: string;
    observed_structure: string;
    visual_notes?: string;
    editing_notes?: string;
    transferable_mechanics: string[];
    pattern_tags: string[];
  }) =>
    request<Benchmark>("/api/v1/intelligence/benchmarks", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  heartbeatRuns: () => request<HeartbeatRun[]>("/api/v1/heartbeat/runs"),
  runHeartbeat: () =>
    request<HeartbeatRun>("/api/v1/heartbeat/run", {
      method: "POST",
      body: JSON.stringify({}),
    }),
  telegramMessages: () => request<TelegramMessage[]>("/api/v1/telegram/messages"),
  captureTelegramFixture: (payload: {
    sender_id: number;
    message_type: "text" | "voice" | "link";
    text?: string;
    transcript?: string;
    source_reference?: string;
  }) =>
    request<TelegramMessage>("/api/v1/telegram/capture-test", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyticsOverview: () =>
    request<AnalyticsOverview>("/api/v1/analytics/overview"),
  importAnalytics: async (formData: FormData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/import`, {
      method: "POST",
      credentials: "include",
      body: formData,
    });
    if (!response.ok) {
      let message = `Import failed (${response.status})`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) message = body.detail;
      } catch {
        // Retain the status fallback.
      }
      throw new ApiError(message, response.status);
    }
    return (await response.json()) as {
      imported: number;
      rejected: number;
      errors: string[];
      insight_ids: string[];
    };
  },
  experiments: () => request<Experiment[]>("/api/v1/analytics/experiments"),
  createExperiment: (payload: {
    title: string;
    question: string;
    hypothesis: string;
    variable: string;
    control_conditions: string[];
    platform: string;
    content_type: string;
    expected_outcome: string;
    success_metric: string;
    measurement_start?: string;
    measurement_end?: string;
  }) =>
    request<Experiment>("/api/v1/analytics/experiments", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  search: (query: string) =>
    request<GlobalSearchResult[]>(
      `/api/v1/search?q=${encodeURIComponent(query)}`,
    ),
};
