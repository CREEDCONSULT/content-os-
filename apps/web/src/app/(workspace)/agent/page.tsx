"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  CircleDollarSign,
  Database,
  FileSearch,
  Route,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { AgentRun } from "@/lib/contracts";

const starterIntents = [
  "Draft a LinkedIn script and three hooks about building BrandOS in public",
  "Review this idea for brand fit and missing evidence",
  "Prepare an internal production plan for the next Builder Walk",
];

export default function AgentConsolePage() {
  const [intent, setIntent] = useState(starterIntents[0] ?? "");
  const [modelBudget, setModelBudget] = useState("0");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const skills = useQuery({ queryKey: ["agent", "skills"], queryFn: api.skills });
  const runs = useQuery({ queryKey: ["agent", "runs"], queryFn: api.agentRuns });
  const createRun = useMutation({
    mutationFn: api.createAgentRun,
    onSuccess: async (run) => {
      setSelectedRunId(run.id);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["agent", "runs"] }),
        queryClient.invalidateQueries({ queryKey: ["approvals"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
      ]);
    },
  });
  const selectedRun = useMemo(
    () =>
      createRun.data?.id === selectedRunId
        ? createRun.data
        : runs.data?.items.find((run) => run.id === selectedRunId) ??
          runs.data?.items[0] ??
          null,
    [createRun.data, runs.data?.items, selectedRunId],
  );

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (intent.trim().length < 3) return;
    createRun.mutate({
      intent: intent.trim(),
      idempotency_key: `dashboard-${crypto.randomUUID()}`,
      budget: {
        model_usd: Number(modelBudget) || 0,
        tool_usd: 0,
      },
      raw_input: { requested_surface: "agent_console" },
    });
  };

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Mezie Brand Director"
        title="Every run explains itself."
        description="Requests are routed through typed skills, grounded in the smallest sufficient canonical context pack, budget-checked, approval-gated, and logged before any meaningful action."
        actions={
          <StatusPill tone="purple" dot>
            {skills.data?.length ?? "—"} governed skills
          </StatusPill>
        }
      />

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <form className="surface p-5 sm:p-6" onSubmit={submit}>
          <div className="flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-xl border border-purple/25 bg-purple/8">
              <BrainCircuit className="size-5 text-purple" />
            </div>
            <div>
              <p className="eyebrow">Run a governed request</p>
              <p className="mt-1 text-xs text-muted">Mock provider is the disclosed default.</p>
            </div>
          </div>
          <label className="mt-6 block">
            <span className="mb-2 block text-xs font-semibold text-muted">Intent</span>
            <textarea
              className="input min-h-32 resize-y"
              value={intent}
              onChange={(event) => setIntent(event.target.value)}
              maxLength={240}
            />
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            {starterIntents.map((item) => (
              <button
                key={item}
                type="button"
                className="focus-ring rounded-full border border-line px-3 py-1.5 text-left text-[0.66rem] text-muted transition hover:border-gold/30 hover:text-ink"
                onClick={() => setIntent(item)}
              >
                {item.split(" ").slice(0, 5).join(" ")}…
              </button>
            ))}
          </div>
          <label className="mt-5 block">
            <span className="mb-2 flex items-center gap-2 text-xs font-semibold text-muted">
              <CircleDollarSign className="size-3.5 text-gold" />
              Requested model budget (USD)
            </span>
            <input
              className="input"
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={modelBudget}
              onChange={(event) => setModelBudget(event.target.value)}
            />
          </label>
          <p className="mt-3 text-[0.68rem] leading-5 text-faint">
            Requests above the configured daily ceiling create an approval record and do not
            call a provider.
          </p>
          <button
            className="button-primary mt-5 w-full"
            type="submit"
            disabled={createRun.isPending || intent.trim().length < 3}
          >
            <Sparkles className="size-4" />
            {createRun.isPending ? "Routing request…" : "Run Brand Director"}
          </button>
          {createRun.isError && (
            <p className="mt-4 rounded-xl border border-danger/25 bg-danger/8 p-3 text-xs text-danger">
              {createRun.error.message}
            </p>
          )}
        </form>

        <RunInspector run={selectedRun} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <div className="surface p-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow">Run ledger</p>
              <h2 className="mt-2 text-xl font-semibold">Recent execution</h2>
            </div>
            <StatusPill>{runs.data?.total ?? 0} total</StatusPill>
          </div>
          {runs.isPending && <div className="mt-5"><LoadingGrid /></div>}
          {runs.isError && (
            <div className="mt-5">
              <ErrorState error={runs.error} retry={() => void runs.refetch()} />
            </div>
          )}
          <div className="mt-5 space-y-2">
            {runs.data?.items.map((run) => (
              <button
                key={run.id}
                type="button"
                onClick={() => setSelectedRunId(run.id)}
                className={`focus-ring w-full rounded-xl border p-3 text-left transition ${
                  selectedRun?.id === run.id
                    ? "border-gold/35 bg-gold/7"
                    : "border-line bg-canvas/45 hover:border-line-bright"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <StatusPill
                    tone={
                      run.status === "completed"
                        ? "green"
                        : run.status === "blocked"
                          ? "gold"
                          : run.status === "failed"
                            ? "danger"
                            : "blue"
                    }
                  >
                    {run.status}
                  </StatusPill>
                  <span className="text-[0.62rem] text-faint">
                    {new Date(run.created_at).toLocaleString("en-CA")}
                  </span>
                </div>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-ink">{run.intent}</p>
                <p className="mt-2 text-[0.64rem] text-faint">
                  {run.provider} · {run.skills_used.length} skills ·{" "}
                  {run.context_loaded.length} sources
                </p>
              </button>
            ))}
          </div>
        </div>

        <div className="surface p-5 sm:p-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="eyebrow">Skill registry</p>
              <h2 className="mt-2 text-xl font-semibold">Typed specialist contracts</h2>
            </div>
            <p className="max-w-md text-right text-xs leading-5 text-muted">
              Version, triggers, tools, context, workflow, output, memory, approval, failure,
              model profile, timeout, and cost class are persisted for every skill.
            </p>
          </div>
          {skills.isPending && <div className="mt-5"><LoadingGrid /></div>}
          {skills.isError && (
            <div className="mt-5">
              <ErrorState error={skills.error} retry={() => void skills.refetch()} />
            </div>
          )}
          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {skills.data?.map((skill) => (
              <article key={skill.id} className="rounded-xl border border-line bg-canvas/45 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[0.62rem] font-semibold text-gold">{skill.slug}</p>
                    <h3 className="mt-1 text-sm font-semibold">{skill.name}</h3>
                  </div>
                  <StatusPill tone={skill.cost_class === "medium" ? "purple" : "neutral"}>
                    {skill.cost_class}
                  </StatusPill>
                </div>
                <p className="mt-3 line-clamp-3 text-xs leading-5 text-muted">
                  {skill.description}
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-[0.62rem] text-faint">
                  <span>{skill.model_profile}</span>
                  <span>·</span>
                  <span>{skill.timeout_seconds}s</span>
                  <span>·</span>
                  <span>v{skill.version}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function RunInspector({ run }: { run: AgentRun | null }) {
  if (!run) {
    return (
      <div className="surface grid min-h-[30rem] place-items-center p-8 text-center">
        <div>
          <Bot className="mx-auto size-9 text-gold" />
          <h2 className="mt-4 text-lg font-semibold">No run selected</h2>
          <p className="mt-2 text-sm text-muted">Start a governed request to inspect its trace.</p>
        </div>
      </div>
    );
  }
  const classifications =
    run.output_envelope.outputs?.provider_output?.classifications ?? [];

  return (
    <article className="surface p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Run transparency</p>
          <h2 className="mt-2 text-xl font-semibold">{run.intent}</h2>
        </div>
        <StatusPill
          tone={
            run.status === "completed"
              ? "green"
              : run.status === "blocked"
                ? "gold"
                : run.status === "failed"
                  ? "danger"
                  : "blue"
          }
          dot
        >
          {run.status}
        </StatusPill>
      </div>
      <p className="mt-4 text-sm leading-6 text-muted">{run.summary}</p>
      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <TraceMetric icon={Route} label="Skills" value={run.skills_used.length} />
        <TraceMetric icon={Database} label="Sources" value={run.context_loaded.length} />
        <TraceMetric icon={CircleDollarSign} label="Cost" value={`$${run.model_cost.toFixed(2)}`} />
        <TraceMetric icon={CheckCircle2} label="Confidence" value={`${Math.round(run.confidence * 100)}%`} />
      </div>
      <div className="mt-5 rounded-xl border border-line bg-canvas/45 p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-ink">
          <FileSearch className="size-4 text-blue" />
          Context loaded
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {run.context_loaded.map((source) => (
            <span
              key={source.version_id}
              className="rounded-full border border-blue/20 bg-blue/5 px-2.5 py-1 text-[0.62rem] text-blue"
            >
              {source.title}
            </span>
          ))}
          {run.context_loaded.length === 0 && (
            <span className="text-xs text-faint">No context records loaded.</span>
          )}
        </div>
      </div>
      {classifications.length > 0 && (
        <div className="mt-5 space-y-2">
          {classifications.map((item) => (
            <div key={`${item.type}-${item.statement}`} className="rounded-xl border border-line p-3">
              <StatusPill tone={item.type === "verified_fact" ? "green" : "purple"}>
                {item.type.replaceAll("_", " ")}
              </StatusPill>
              <p className="mt-2 text-xs leading-5 text-ink">{item.statement}</p>
              <p className="mt-1 text-[0.64rem] text-faint">{item.evidence}</p>
            </div>
          ))}
        </div>
      )}
      {run.approvals_required.length > 0 && (
        <div className="mt-5 rounded-xl border border-gold/25 bg-gold/7 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gold-bright">
            <ShieldAlert className="size-4" />
            Human approval required
          </div>
          <p className="mt-2 text-xs text-muted">
            {run.approvals_required.map((item) => item.action_type.replaceAll("_", " ")).join(", ")}
          </p>
        </div>
      )}
      <div className="mt-5 flex flex-wrap gap-2">
        {run.skills_used.map((skill) => (
          <span
            key={skill}
            className="rounded-full border border-line bg-panel-soft px-2.5 py-1 text-[0.62rem] text-muted"
          >
            {skill}
          </span>
        ))}
      </div>
      {run.next_actions.map((action) => (
        <div key={action} className="mt-3 flex gap-2 text-xs text-muted">
          <ArrowRight className="mt-0.5 size-3.5 shrink-0 text-gold" />
          {action}
        </div>
      ))}
    </article>
  );
}

function TraceMetric({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border border-line bg-canvas/45 p-3">
      <Icon className="size-4 text-gold" />
      <p className="mt-3 text-[0.62rem] text-faint">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}
