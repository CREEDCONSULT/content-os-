import type {
  Approval,
  AuthUser,
  BrandDocument,
  BrandDocumentDetail,
  ContentItem,
  ContentList,
  DashboardSummary,
  Idea,
  IdeaList,
  Integration,
  PipelineStatus,
} from "@/lib/contracts";

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
  createIdea: (payload: {
    title: string;
    raw_input: string;
    pillar?: string;
    audience: string;
    platform_fit: string[];
  }) =>
    request<Idea>("/api/v1/ideas", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
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
};
