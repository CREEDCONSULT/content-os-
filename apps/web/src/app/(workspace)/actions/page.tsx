"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bot,
  Check,
  CheckCircle2,
  Clock3,
  DatabaseZap,
  ExternalLink,
  FileJson2,
  Inbox,
  Play,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  X,
} from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { AgentToolCall, Approval, ProposedDashboardAction } from "@/lib/contracts";

const lanes = [
  {
    id: "proposed",
    label: "Ready",
    description: "Agent proposals waiting for a deliberate execute click.",
  },
  {
    id: "approval_required",
    label: "Needs approval",
    description: "Risky actions paused behind a human approval record.",
  },
  {
    id: "executed",
    label: "Executed",
    description: "Safe internal tools that already wrote to BrandOS.",
  },
  {
    id: "all",
    label: "All",
    description: "Every proposal in the inbox.",
  },
] as const;

type LaneId = (typeof lanes)[number]["id"];

export default function AgentActionInboxPage() {
  const [lane, setLane] = useState<LaneId>("proposed");
  const queryClient = useQueryClient();
  const proposals = useQuery({
    queryKey: ["actions", "proposals"],
    queryFn: () => api.actionProposals(),
  });
  const toolCalls = useQuery({
    queryKey: ["actions", "tool-calls"],
    queryFn: api.actionToolCalls,
  });
  const pendingApprovals = useQuery({
    queryKey: ["approvals", "pending", "action-inbox"],
    queryFn: () => api.approvals("pending"),
  });
  const approvedApprovals = useQuery({
    queryKey: ["approvals", "approved", "action-inbox"],
    queryFn: () => api.approvals("approved"),
  });
  const rejectedApprovals = useQuery({
    queryKey: ["approvals", "rejected", "action-inbox"],
    queryFn: () => api.approvals("rejected"),
  });

  const execute = useMutation({
    mutationFn: api.executeActionProposal,
    onSuccess: async () => {
      await invalidateActionState(queryClient);
    },
  });
  const decision = useMutation({
    mutationFn: ({
      approvalId,
      value,
      notes,
    }: {
      approvalId: string;
      value: "approved" | "rejected";
      notes?: string;
    }) => api.decideApproval(approvalId, value, notes),
    onSuccess: async () => {
      await invalidateActionState(queryClient);
    },
  });

  const actions = useMemo(() => proposals.data?.items ?? [], [proposals.data]);
  const visibleActions = useMemo(
    () => (lane === "all" ? actions : actions.filter((action) => action.status === lane)),
    [actions, lane],
  );
  const approvalsById = useMemo(() => {
    const records = [
      ...(pendingApprovals.data ?? []),
      ...(approvedApprovals.data ?? []),
      ...(rejectedApprovals.data ?? []),
    ].filter((approval) => approval.target_type === "proposed_dashboard_action");
    return new Map(records.map((approval) => [approval.id, approval]));
  }, [approvedApprovals.data, pendingApprovals.data, rejectedApprovals.data]);

  const metrics = useMemo(
    () => ({
      proposed: actions.filter((action) => action.status === "proposed").length,
      approvalRequired: actions.filter((action) => action.status === "approval_required").length,
      executed: actions.filter((action) => action.status === "executed").length,
      blockedCalls: (toolCalls.data ?? []).filter((call) => call.status === "blocked").length,
    }),
    [actions, toolCalls.data],
  );

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Agent Action Inbox"
        title="Review the agent's proposed moves before anything changes."
        description="This is the visual control room between rough conversation and dashboard state. Safe internal proposals can execute here; public, paid, canonical, external, or sensitive actions become approval gates."
        actions={
          <button
            className="button-secondary"
            type="button"
            onClick={() => {
              void proposals.refetch();
              void toolCalls.refetch();
              void pendingApprovals.refetch();
              void approvedApprovals.refetch();
              void rejectedApprovals.refetch();
            }}
          >
            <RefreshCw className="size-4" />
            Refresh
          </button>
        }
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Action inbox metrics">
        <MetricCard
          icon={Inbox}
          label="Ready proposals"
          value={metrics.proposed}
          tone="blue"
          detail="Awaiting an execute decision"
        />
        <MetricCard
          icon={ShieldAlert}
          label="Approval gates"
          value={metrics.approvalRequired}
          tone="gold"
          detail="Human review before execution"
        />
        <MetricCard
          icon={CheckCircle2}
          label="Executed safely"
          value={metrics.executed}
          tone="green"
          detail="Internal writes completed"
        />
        <MetricCard
          icon={DatabaseZap}
          label="Blocked tool calls"
          value={metrics.blockedCalls}
          tone="purple"
          detail="Paused by policy"
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(21rem,0.72fr)]">
        <div className="space-y-5">
          <div className="surface p-2">
            <div className="grid gap-2 md:grid-cols-4">
              {lanes.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  aria-label={item.label}
                  aria-pressed={lane === item.id}
                  onClick={() => setLane(item.id)}
                  className={`focus-ring rounded-xl border p-4 text-left transition ${
                    lane === item.id
                      ? "border-gold/35 bg-gold/8"
                      : "border-transparent hover:border-line hover:bg-panel-soft"
                  }`}
                >
                  <span className="text-xs font-semibold text-ink">{item.label}</span>
                  <span className="mt-1 block text-[0.66rem] leading-4 text-faint">
                    {item.description}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {execute.isError && (
            <div className="rounded-xl border border-danger/25 bg-danger/8 p-4 text-sm text-danger">
              {execute.error.message}
            </div>
          )}
          {decision.isError && (
            <div className="rounded-xl border border-danger/25 bg-danger/8 p-4 text-sm text-danger">
              {decision.error.message}
            </div>
          )}
          {proposals.isPending && <LoadingGrid />}
          {proposals.isError && (
            <ErrorState error={proposals.error} retry={() => void proposals.refetch()} />
          )}
          {proposals.data && visibleActions.length === 0 && (
            <div className="surface flex min-h-56 flex-col items-center justify-center p-8 text-center">
              <DatabaseZap className="size-8 text-gold" aria-hidden />
              <h2 className="mt-4 text-lg font-semibold">No proposals in this lane.</h2>
              <p className="mt-2 max-w-lg text-sm text-muted">
                Agent proposals will appear here after a conversation or agent run returns a
                safe dashboard action. For the strongest end-to-end test, ask the Brand Director
                to prepare a 10-day campaign.
              </p>
              <Link className="button-secondary mt-5" href="/agent">
                Run Brand Director
                <ExternalLink className="size-3.5" />
              </Link>
            </div>
          )}
          {visibleActions.length > 0 && (
            <div className="grid gap-4">
              {visibleActions.map((action) => (
                <ActionCard
                  key={action.id}
                  action={action}
                  approval={action.approval_id ? approvalsById.get(action.approval_id) : undefined}
                  executing={execute.isPending && execute.variables === action.id}
                  deciding={
                    decision.isPending && decision.variables?.approvalId === action.approval_id
                  }
                  onExecute={() => execute.mutate(action.id)}
                  onDecision={(approvalId, value, notes) =>
                    decision.mutate({ approvalId, value, notes })
                  }
                />
              ))}
            </div>
          )}
        </div>

        <aside className="space-y-5">
          <section className="surface p-5 sm:p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="eyebrow">Execution trail</p>
                <h2 className="mt-2 text-lg font-semibold">Recent tool calls</h2>
              </div>
              <Bot className="size-5 text-purple" />
            </div>
            {toolCalls.isPending && (
              <div className="mt-5 space-y-3">
                <div className="skeleton h-16 rounded-xl" />
                <div className="skeleton h-16 rounded-xl" />
              </div>
            )}
            {toolCalls.isError && (
              <div className="mt-5 rounded-xl border border-danger/25 bg-danger/8 p-3 text-xs text-danger">
                {toolCalls.error.message}
              </div>
            )}
            <div className="mt-5 space-y-3">
              {(toolCalls.data ?? []).slice(0, 6).map((call) => (
                <ToolCallCard key={call.id} call={call} />
              ))}
              {toolCalls.data?.length === 0 && (
                <p className="rounded-xl border border-line bg-canvas/45 p-4 text-xs leading-5 text-muted">
                  No tool calls yet. Execute a safe proposal or create an approval gate to
                  populate this ledger.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-2xl border border-gold/20 bg-gold/6 p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-gold-bright">
              <ShieldCheck className="size-4" />
              Safety boundary
            </div>
            <p className="mt-3 text-xs leading-5 text-muted">
              Approval means the human decision is recorded. It does not magically publish,
              spend, outreach, promote canonical memory, or schedule externally until the
              matching adapter and resumable job runner are intentionally built.
            </p>
            <Link className="button-ghost mt-4 min-h-8 px-0 text-xs" href="/approvals">
              Open full approval queue
              <ExternalLink className="size-3.5" />
            </Link>
          </section>
        </aside>
      </section>
    </div>
  );
}

async function invalidateActionState(queryClient: ReturnType<typeof useQueryClient>) {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ["actions"] }),
    queryClient.invalidateQueries({ queryKey: ["approvals"] }),
    queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
    queryClient.invalidateQueries({ queryKey: ["ideas"] }),
  ]);
}

function ActionCard({
  action,
  approval,
  executing,
  deciding,
  onExecute,
  onDecision,
}: {
  action: ProposedDashboardAction;
  approval?: Approval;
  executing: boolean;
  deciding: boolean;
  onExecute: () => void;
  onDecision: (approvalId: string, value: "approved" | "rejected", notes?: string) => void;
}) {
  const [notes, setNotes] = useState("");
  const isSafeExecutable = action.action_type === "create_rough_idea" && action.risk_level === "low";
  const isCampaign = action.action_type === "create_campaign_plan";
  const title =
    typeof action.payload.title === "string"
      ? action.payload.title
      : typeof action.payload.campaign_name === "string"
        ? action.payload.campaign_name
        : formatAction(action.action_type);
  const approvalStatus = approval?.status;

  return (
    <article className="surface overflow-hidden p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap gap-2">
            <StatusPill tone={statusTone(action.status)} dot>
              {action.status.replaceAll("_", " ")}
            </StatusPill>
            <StatusPill tone={riskTone(action.risk_level)}>{action.risk_level} risk</StatusPill>
            {action.is_demo && <StatusPill>Demo</StatusPill>}
          </div>
          <p className="eyebrow mt-5">{formatAction(action.action_type)}</p>
          <h2 className="mt-2 text-xl font-semibold leading-tight">{title}</h2>
        </div>
        <span className="flex items-center gap-1.5 text-[0.68rem] text-faint">
          <Clock3 className="size-3.5" />
          {new Date(action.created_at).toLocaleString("en-CA", {
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>

      <p className="mt-4 text-sm leading-6 text-muted">{action.rationale}</p>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <Fact label="Target" value={action.target_type ?? "No target yet"} />
        <Fact label="Record" value={action.target_id ? action.target_id.slice(0, 12) : "Pending"} />
        <Fact
          label="Agent run"
          value={action.agent_run_id ? action.agent_run_id.slice(0, 12) : "Manual/API"}
        />
      </div>

      {approval && (
        <div className="mt-5 rounded-xl border border-gold/25 bg-gold/7 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gold-bright">
              <ShieldAlert className="size-4" />
              Approval gate: {approval.status}
            </div>
            <span className="text-[0.65rem] text-faint">#{approval.id.slice(0, 12)}</span>
          </div>
          {approval.status === "pending" ? (
            <>
              <label className="mt-4 block">
                <span className="mb-2 block text-xs font-semibold text-muted">
                  Decision notes
                </span>
                <textarea
                  className="input min-h-20 resize-y"
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                  placeholder="Optional rationale for approving or rejecting this proposed action..."
                />
              </label>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <button
                  className="button-danger"
                  type="button"
                  disabled={deciding}
                  onClick={() => onDecision(approval.id, "rejected", notes || undefined)}
                >
                  <X className="size-4" />
                  Reject
                </button>
                <button
                  className="button-primary"
                  type="button"
                  disabled={deciding}
                  onClick={() => onDecision(approval.id, "approved", notes || undefined)}
                >
                  <Check className="size-4" />
                  Approve
                </button>
              </div>
            </>
          ) : (
            <p className="mt-3 flex items-center gap-2 text-xs leading-5 text-muted">
              {approval.status === "approved" ? (
                <ShieldCheck className="size-4 shrink-0 text-green" />
              ) : (
                <ShieldX className="size-4 shrink-0 text-danger" />
              )}
              Decided by {approval.approved_by ?? "unknown"}.{" "}
              {approval.notes ? `Notes: ${approval.notes}` : "No notes were added."}
            </p>
          )}
        </div>
      )}

      <div className="mt-5 grid gap-3 lg:grid-cols-2">
        <JsonPreview title="Payload" value={action.payload} />
        <JsonPreview title="Result" value={action.result_json} />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-5">
        <p className="max-w-xl text-xs leading-5 text-faint">
          {action.status === "executed"
            ? "This safe internal write has completed and is now represented in BrandOS."
            : action.status === "approval_required"
              ? approvalStatus === "approved"
                ? "Human approval is recorded. External execution remains paused until the matching adapter exists."
                : "This action is intentionally paused behind human approval."
              : isSafeExecutable || isCampaign
                ? isCampaign
                  ? "This will stage an internal campaign plan, content records, calendar planning blocks, and experiments. It will not publish, spend, or contact anyone."
                  : "This will create an internal rough idea. It will not publish, spend, or contact anyone."
                : "Executing this proposal will create an approval gate instead of performing the risky action."}
        </p>
        {action.status === "proposed" && (
          <button className="button-primary" type="button" disabled={executing} onClick={onExecute}>
            <Play className="size-4" />
            {executing
              ? "Processing..."
              : isSafeExecutable || isCampaign
                ? "Execute safe write"
                : "Create approval gate"}
          </button>
        )}
        {action.status === "approval_required" && !approval && (
          <Link className="button-secondary" href="/approvals">
            <ShieldAlert className="size-4" />
            Find approval
          </Link>
        )}
      </div>
    </article>
  );
}

function ToolCallCard({ call }: { call: AgentToolCall }) {
  return (
    <article className="rounded-xl border border-line bg-canvas/45 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold">{formatAction(call.tool_name)}</p>
          <p className="mt-1 text-[0.64rem] text-faint">{call.tool_type.replaceAll("_", " ")}</p>
        </div>
        <StatusPill tone={statusTone(call.status)}>{call.status}</StatusPill>
      </div>
      <p className="mt-3 text-[0.64rem] text-faint">
        {new Date(call.created_at).toLocaleString("en-CA")}{" "}
        {call.approval_id ? `· approval ${call.approval_id.slice(0, 8)}` : ""}
      </p>
    </article>
  );
}

function JsonPreview({ title, value }: { title: string; value: Record<string, unknown> }) {
  const hasValue = Object.keys(value).length > 0;
  return (
    <details className="rounded-xl border border-line bg-[#080b10] p-4">
      <summary className="flex cursor-pointer items-center gap-2 text-xs font-semibold text-muted">
        <FileJson2 className="size-4 text-blue" />
        {title}
      </summary>
      <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap text-[0.68rem] leading-5 text-faint">
        {hasValue ? JSON.stringify(value, null, 2) : "No data recorded yet."}
      </pre>
    </details>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  tone,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
  detail: string;
  tone: "blue" | "gold" | "green" | "purple";
}) {
  const toneClass = {
    blue: "border-blue/25 bg-blue/7 text-blue",
    gold: "border-gold/25 bg-gold/7 text-gold",
    green: "border-green/25 bg-green/7 text-green",
    purple: "border-purple/25 bg-purple/7 text-purple",
  }[tone];
  return (
    <article className="surface p-5">
      <div className={`grid size-10 place-items-center rounded-xl border ${toneClass}`}>
        <Icon className="size-5" />
      </div>
      <p className="mt-5 text-[0.65rem] font-bold uppercase tracking-[0.12em] text-faint">
        {label}
      </p>
      <strong className="mt-2 block font-display text-3xl font-semibold">{value}</strong>
      <p className="mt-1 text-xs text-muted">{detail}</p>
    </article>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-line bg-canvas/45 p-3">
      <span className="text-[0.62rem] font-semibold uppercase tracking-[0.1em] text-faint">
        {label}
      </span>
      <span className="mt-1 block truncate text-xs text-ink">{value}</span>
    </div>
  );
}

function formatAction(value: string) {
  return value.replaceAll("_", " ");
}

function statusTone(
  status: string,
): "gold" | "green" | "blue" | "purple" | "danger" | "neutral" {
  if (status === "executed" || status === "completed" || status === "approved") return "green";
  if (status === "approval_required" || status === "blocked") return "gold";
  if (status === "failed" || status === "rejected") return "danger";
  if (status === "proposed" || status === "running") return "blue";
  return "neutral";
}

function riskTone(
  risk: ProposedDashboardAction["risk_level"],
): "gold" | "green" | "blue" | "purple" | "danger" | "neutral" {
  if (risk === "critical" || risk === "high") return "danger";
  if (risk === "medium") return "gold";
  return "blue";
}
