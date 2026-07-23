"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Clock3, ShieldCheck, ShieldX, X } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { Approval } from "@/lib/contracts";

export default function ApprovalsPage() {
  const [status, setStatus] = useState<"pending" | "approved" | "rejected">("pending");
  const queryClient = useQueryClient();
  const approvals = useQuery({
    queryKey: ["approvals", status],
    queryFn: () => api.approvals(status),
  });
  const decision = useMutation({
    mutationFn: ({
      id,
      value,
      notes,
    }: {
      id: string;
      value: "approved" | "rejected";
      notes?: string;
    }) => api.decideApproval(id, value, notes),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["approvals"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        queryClient.invalidateQueries({ queryKey: ["content"] }),
        queryClient.invalidateQueries({ queryKey: ["brand-documents"] }),
      ]);
    },
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Approval Queue"
        title="High-impact actions stop here first."
        description="Canonical changes, publishing, costly integrations, and other consequential actions require a durable backend approval record—not a cosmetic frontend confirmation."
        actions={
          <StatusPill tone="gold" dot>
            {approvals.data?.length ?? "—"} {status}
          </StatusPill>
        }
      />

      <div className="inline-flex rounded-xl border border-line bg-panel p-1">
        {(["pending", "approved", "rejected"] as const).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setStatus(item)}
            className={`focus-ring rounded-lg px-4 py-2 text-xs font-semibold capitalize transition ${
              status === item ? "bg-gold/12 text-gold-bright" : "text-muted hover:text-ink"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {decision.isError && (
        <div className="rounded-xl border border-danger/25 bg-danger/8 p-4 text-sm text-danger">
          {decision.error.message}
        </div>
      )}
      {approvals.isPending && <LoadingGrid />}
      {approvals.isError && (
        <ErrorState error={approvals.error} retry={() => void approvals.refetch()} />
      )}
      {approvals.data?.length === 0 && (
        <EmptyState
          title={`No ${status} approvals.`}
          body={
            status === "pending"
              ? "The queue is clear. Consequential actions will appear here before execution."
              : `No approval records currently have a ${status} decision.`
          }
        />
      )}
      {approvals.data && approvals.data.length > 0 && (
        <section className="grid gap-4 xl:grid-cols-2">
          {approvals.data.map((approval) => (
            <ApprovalCard
              key={approval.id}
              approval={approval}
              deciding={decision.isPending && decision.variables?.id === approval.id}
              onDecision={(value, notes) =>
                decision.mutate({ id: approval.id, value, notes })
              }
            />
          ))}
        </section>
      )}
    </div>
  );
}

function ApprovalCard({
  approval,
  deciding,
  onDecision,
}: {
  approval: Approval;
  deciding: boolean;
  onDecision: (value: "approved" | "rejected", notes?: string) => void;
}) {
  const [notes, setNotes] = useState("");
  const riskTone =
    approval.risk_level === "critical" || approval.risk_level === "high"
      ? "danger"
      : approval.risk_level === "medium"
        ? "gold"
        : "blue";

  return (
    <article className="surface p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex gap-2">
          <StatusPill tone={riskTone}>{approval.risk_level} risk</StatusPill>
          <StatusPill>{approval.status}</StatusPill>
        </div>
        <span className="flex items-center gap-1.5 text-[0.68rem] text-faint">
          <Clock3 className="size-3.5" />
          {new Date(approval.created_at).toLocaleDateString("en-CA")}
        </span>
      </div>
      <p className="eyebrow mt-6">{approval.action_type.replaceAll("_", " ")}</p>
      <h2 className="mt-2 text-lg font-semibold">
        {approval.target_type}: {approval.target_id.slice(0, 12)}
      </h2>
      <div className="mt-4 grid gap-3 rounded-xl border border-line bg-canvas/45 p-4 text-xs text-muted sm:grid-cols-2">
        <div>
          <span className="block text-faint">Requested by</span>
          <span className="mt-1 block text-ink">{approval.requested_by}</span>
        </div>
        <div>
          <span className="block text-faint">Cost ceiling</span>
          <span className="mt-1 block text-ink">${approval.cost_estimate.toFixed(2)}</span>
        </div>
      </div>
      {Object.keys(approval.context).length > 0 && (
        <pre className="mt-4 max-h-36 overflow-auto whitespace-pre-wrap rounded-xl border border-line bg-[#080b10] p-4 text-[0.68rem] leading-5 text-muted">
          {JSON.stringify(approval.context, null, 2)}
        </pre>
      )}
      {approval.status === "pending" ? (
        <>
          <label className="mt-4 block">
            <span className="mb-2 block text-xs font-semibold text-muted">Decision notes</span>
            <textarea
              className="input min-h-20 resize-y"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Optional rationale for the durable audit trail…"
            />
          </label>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <button
              className="button-danger"
              type="button"
              disabled={deciding}
              onClick={() => onDecision("rejected", notes || undefined)}
            >
              <X className="size-4" />
              Reject
            </button>
            <button
              className="button-primary"
              type="button"
              disabled={deciding}
              onClick={() => onDecision("approved", notes || undefined)}
            >
              <Check className="size-4" />
              Approve
            </button>
          </div>
        </>
      ) : (
        <div className="mt-5 flex items-center gap-2 text-sm text-muted">
          {approval.status === "approved" ? (
            <ShieldCheck className="size-4 text-green" />
          ) : (
            <ShieldX className="size-4 text-danger" />
          )}
          Decided by {approval.approved_by ?? "unknown"} · {approval.notes || "No notes"}
        </div>
      )}
    </article>
  );
}
