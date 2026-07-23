"use client";

import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  Bot,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Layers3,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { DashboardMetric, PipelineGroup } from "@/lib/contracts";

const metricAccents: Record<string, string> = {
  blue: "from-blue/16 border-blue/25 text-blue",
  gold: "from-gold/16 border-gold/25 text-gold",
  green: "from-green/16 border-green/25 text-green",
  purple: "from-purple/16 border-purple/25 text-purple",
};

const pipelineLabels: Record<PipelineGroup, string> = {
  ideation: "Ideation",
  scripting: "Scripting",
  production: "Production",
  review: "Review",
  published: "Published",
};

export default function DashboardPage() {
  const summary = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.dashboard,
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Command center"
        title={summary.data ? `Good to see you, ${summary.data.greeting_name}.` : "Your brand at a glance."}
        description={
          summary.data?.signature_line ??
          "A live operational view of brand intelligence, production, decisions, and momentum."
        }
        actions={
          <Link className="button-secondary w-fit" href="/approvals">
            <ShieldAlert className="size-4 text-gold" />
            {summary.data?.pending_approvals ?? "—"} approvals
          </Link>
        }
      />

      {summary.isPending && <LoadingGrid />}
      {summary.isError && <ErrorState error={summary.error} retry={() => void summary.refetch()} />}

      {summary.data && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Operating metrics">
            {summary.data.metrics.map((metric) => (
              <MetricCard key={metric.label} metric={metric} />
            ))}
          </section>

          <section className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(22rem,0.8fr)]">
            <div className="surface p-5 sm:p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="eyebrow">Lifecycle pulse</p>
                  <h2 className="mt-2 text-xl font-semibold">Work moving through the system</h2>
                </div>
                <Link className="button-ghost min-h-8 text-xs" href="/pipeline">
                  Open pipeline
                  <ArrowRight className="size-3.5" />
                </Link>
              </div>
              <div className="mt-7 grid gap-3 sm:grid-cols-5">
                {(Object.entries(pipelineLabels) as [PipelineGroup, string][]).map(
                  ([key, label], index) => {
                    const value = summary.data.pipeline_groups[key] ?? 0;
                    return (
                      <div
                        key={key}
                        className="relative overflow-hidden rounded-xl border border-line bg-canvas/45 p-4"
                      >
                        <span className="text-[0.63rem] font-bold uppercase tracking-[0.12em] text-faint">
                          {label}
                        </span>
                        <div className="mt-3 flex items-end justify-between">
                          <strong className="font-display text-3xl font-semibold">{value}</strong>
                          <span className="text-[0.62rem] text-faint">0{index + 1}</span>
                        </div>
                        <div
                          className="absolute inset-x-0 bottom-0 h-0.5 bg-gradient-to-r from-gold/80 to-transparent"
                          style={{ opacity: Math.max(0.25, value / 5) }}
                        />
                      </div>
                    );
                  },
                )}
              </div>
            </div>

            <div className="surface p-5 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Autonomous agent</p>
                  <h2 className="mt-2 text-xl font-semibold">Operating posture</h2>
                </div>
                <Bot className="size-6 text-purple" />
              </div>
              <div className="mt-6 rounded-xl border border-purple/20 bg-purple/5 p-4">
                <div className="flex items-center justify-between gap-3">
                  <StatusPill tone="purple" dot>
                    {summary.data.agent.status}
                  </StatusPill>
                  {summary.data.agent.is_mock && <StatusPill>Mock</StatusPill>}
                </div>
                <p className="mt-4 text-sm font-medium leading-6">{summary.data.agent.current_focus}</p>
                <p className="mt-2 text-xs text-faint">
                  Model alias: {summary.data.agent.model_alias}
                </p>
              </div>
              <p className="mt-4 text-xs leading-5 text-muted">
                Agent actions remain bounded by approval, provider, budget, and provenance contracts.
              </p>
            </div>
          </section>

          <section className="grid gap-5 xl:grid-cols-3">
            <DashboardList
              title="Today"
              eyebrow="Priority stack"
              icon={<CheckCircle2 className="size-4 text-green" />}
              empty="No open tasks in the active stack."
            >
              {summary.data.today.map((task) => (
                <li key={task.id} className="flex gap-3 border-t border-line py-3 first:border-0">
                  <span className="mt-1 size-2 shrink-0 rounded-full bg-gold" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{task.title}</p>
                    <p className="mt-1 text-[0.68rem] uppercase tracking-[0.08em] text-faint">
                      {task.priority} · {task.status}
                    </p>
                  </div>
                </li>
              ))}
            </DashboardList>

            <DashboardList
              title="Recent activity"
              eyebrow="Audit trail"
              icon={<Clock3 className="size-4 text-blue" />}
              empty="No operational events recorded."
            >
              {summary.data.recent_activity.map((event) => (
                <li key={event.id} className="border-t border-line py-3 first:border-0">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm leading-5">{event.summary}</p>
                    {event.is_demo && <StatusPill>Demo</StatusPill>}
                  </div>
                  <p className="mt-1 text-[0.68rem] text-faint">{formatDateTime(event.created_at)}</p>
                </li>
              ))}
            </DashboardList>

            <DashboardList
              title="Upcoming content"
              eyebrow="Schedule"
              icon={<CalendarDays className="size-4 text-gold" />}
              empty="No content currently carries a due date."
            >
              {summary.data.upcoming_content.map((item) => (
                <li key={item.id} className="border-t border-line py-3 first:border-0">
                  <p className="text-sm font-medium">{item.title}</p>
                  <div className="mt-2 flex items-center justify-between gap-3">
                    <span className="text-[0.68rem] text-faint">
                      {item.platform} · {item.due_date ?? "Unscheduled"}
                    </span>
                    <StatusPill tone="gold">{item.status.replaceAll("_", " ")}</StatusPill>
                  </div>
                </li>
              ))}
            </DashboardList>
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({ metric }: { metric: DashboardMetric }) {
  return (
    <article
      className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br to-panel p-5 ${metricAccents[metric.accent] ?? metricAccents.gold}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-[0.1em] text-muted">
          {metric.label}
        </span>
        {metric.is_demo && <StatusPill>Demo</StatusPill>}
      </div>
      <div className="mt-5 flex items-end justify-between">
        <strong className="font-display text-4xl font-semibold text-ink">{metric.value}</strong>
        <Layers3 className="size-4 opacity-70" />
      </div>
      <p className="mt-3 text-xs text-muted">{metric.delta}</p>
    </article>
  );
}

function DashboardList({
  eyebrow,
  title,
  icon,
  empty,
  children,
}: {
  eyebrow: string;
  title: string;
  icon: React.ReactNode;
  empty: string;
  children: React.ReactNode[];
}) {
  return (
    <section className="surface p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2 className="mt-1.5 text-lg font-semibold">{title}</h2>
        </div>
        {icon}
      </div>
      <ul className="mt-4">
        {children.length > 0 ? children : <li className="py-6 text-sm text-muted">{empty}</li>}
      </ul>
    </section>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-CA", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
