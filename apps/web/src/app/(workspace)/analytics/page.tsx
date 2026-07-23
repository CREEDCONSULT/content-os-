"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BarChart3,
  Beaker,
  FileUp,
  Lightbulb,
  MousePointerClick,
  Save,
  Share2,
} from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const queryClient = useQueryClient();
  const overview = useQuery({ queryKey: ["analytics"], queryFn: api.analyticsOverview });
  const experiments = useQuery({ queryKey: ["experiments"], queryFn: api.experiments });
  const [csv, setCsv] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [question, setQuestion] = useState("");
  const [hypothesis, setHypothesis] = useState("");
  const [variable, setVariable] = useState("");
  const [controls, setControls] = useState("Same topic\nSame duration\nSame production quality");
  const [metric, setMetric] = useState("Save rate");

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["analytics"] }),
      queryClient.invalidateQueries({ queryKey: ["experiments"] }),
    ]);
  };
  const importCsv = useMutation({
    mutationFn: api.importAnalytics,
    onSuccess: async (result) => {
      setImportResult(`${result.imported} imported · ${result.rejected} rejected`);
      setCsv(null);
      await refresh();
    },
  });
  const createExperiment = useMutation({
    mutationFn: api.createExperiment,
    onSuccess: async () => {
      setTitle("");
      setQuestion("");
      setHypothesis("");
      setVariable("");
      await refresh();
    },
  });

  const submitCsv = (event: FormEvent) => {
    event.preventDefault();
    if (!csv) return;
    const formData = new FormData();
    formData.set("file", csv);
    importCsv.mutate(formData);
  };
  const submitExperiment = (event: FormEvent) => {
    event.preventDefault();
    createExperiment.mutate({
      title,
      question,
      hypothesis,
      variable,
      control_conditions: controls
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      platform: "Instagram",
      content_type: "Builder Walk",
      expected_outcome: `A measurable change in ${metric.toLowerCase()}.`,
      success_metric: metric,
    });
  };

  const loading = overview.isPending || experiments.isPending;
  const error = overview.error ?? experiments.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Analytics and learning · Observation before doctrine"
        title="Turn performance records into testable learning."
        description="Metrics can be entered through a normalized CSV, insights remain working hypotheses, and experiments isolate one variable with explicit controls before any learning is promoted."
        actions={<StatusPill tone="blue">{overview.data?.metrics.length ?? 0} snapshots</StatusPill>}
      />

      {loading && <LoadingGrid />}
      {error && <ErrorState error={error} retry={() => void refresh()} />}

      {!loading && !error && overview.data && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <Metric icon={BarChart3} label="Views" value={overview.data.totals.views} />
            <Metric
              icon={MousePointerClick}
              label="Engagement"
              value={overview.data.totals.engagement}
            />
            <Metric icon={Save} label="Saves" value={overview.data.totals.saves} />
            <Metric icon={Share2} label="Shares" value={overview.data.totals.shares} />
            <Metric
              icon={Beaker}
              label="Experiments"
              value={experiments.data?.length ?? 0}
            />
          </section>

          <section className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
            <div className="space-y-5">
              <form className="surface p-5" onSubmit={submitCsv}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Metric import</p>
                    <h2 className="mt-2 text-lg font-semibold">Normalize a CSV</h2>
                  </div>
                  <FileUp className="size-5 text-blue" />
                </div>
                <input
                  className="input mt-5 file:mr-3 file:rounded-md file:border-0 file:bg-blue/10 file:px-2 file:py-1 file:text-xs file:text-blue"
                  type="file"
                  accept=".csv,text/csv"
                  required
                  onChange={(event) => setCsv(event.target.files?.[0] ?? null)}
                />
                <p className="mt-3 text-[0.65rem] leading-5 text-faint">
                  Required columns: platform, views, impressions, engagement, saves, shares.
                  Optional: captured_at, content_item_id, watch_time_seconds.
                </p>
                <button
                  className="button-secondary mt-4 w-full"
                  type="submit"
                  disabled={!csv || importCsv.isPending}
                >
                  <FileUp className="size-4" />
                  Import and validate
                </button>
                {importResult && <p className="mt-3 text-xs text-green">{importResult}</p>}
                {importCsv.isError && (
                  <p className="mt-3 text-xs text-danger">{importCsv.error.message}</p>
                )}
              </form>

              <div className="surface p-5">
                <p className="eyebrow">Platform breakdown</p>
                <div className="mt-4 space-y-3">
                  {overview.data.platform_breakdown.map((platform) => (
                    <article key={platform.platform} className="rounded-xl border border-line p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold">{platform.platform}</p>
                        <StatusPill tone="blue">{platform.records} records</StatusPill>
                      </div>
                      <div className="mt-3 grid grid-cols-3 gap-2 text-[0.65rem] text-faint">
                        <span>{platform.views.toLocaleString()} views</span>
                        <span>{platform.saves.toLocaleString()} saves</span>
                        <span>{platform.shares.toLocaleString()} shares</span>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-5">
              <div className="surface p-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Working insights</p>
                    <h2 className="mt-2 text-lg font-semibold">What the records may suggest</h2>
                  </div>
                  <Lightbulb className="size-5 text-gold" />
                </div>
                <div className="mt-5 space-y-3">
                  {overview.data.insights.map((insight) => (
                    <article key={insight.id} className="rounded-xl border border-line p-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <StatusPill tone="gold">{insight.classification}</StatusPill>
                        <StatusPill>{Math.round(insight.confidence * 100)}% confidence</StatusPill>
                        {insight.is_demo && <StatusPill>Demo</StatusPill>}
                      </div>
                      <h3 className="mt-3 text-sm font-semibold">{insight.title}</h3>
                      <p className="mt-2 text-xs leading-5 text-muted">{insight.observation}</p>
                      <div className="mt-3 rounded-lg bg-gold/5 p-3 text-xs leading-5 text-gold-bright">
                        Hypothesis: {insight.hypothesis}
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              <form className="surface p-5 sm:p-6" onSubmit={submitExperiment}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Experiment manager</p>
                    <h2 className="mt-2 text-lg font-semibold">Test one primary variable</h2>
                  </div>
                  <Beaker className="size-5 text-purple" />
                </div>
                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <Field label="Experiment title">
                    <input
                      className="input"
                      required
                      minLength={3}
                      value={title}
                      onChange={(event) => setTitle(event.target.value)}
                    />
                  </Field>
                  <Field label="Primary variable">
                    <input
                      className="input"
                      required
                      minLength={2}
                      value={variable}
                      placeholder="Hook type"
                      onChange={(event) => setVariable(event.target.value)}
                    />
                  </Field>
                  <Field label="Question">
                    <textarea
                      className="input min-h-24 resize-y"
                      required
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                    />
                  </Field>
                  <Field label="Hypothesis">
                    <textarea
                      className="input min-h-24 resize-y"
                      required
                      value={hypothesis}
                      onChange={(event) => setHypothesis(event.target.value)}
                    />
                  </Field>
                  <Field label="Control conditions · one per line">
                    <textarea
                      className="input min-h-24 resize-y"
                      required
                      value={controls}
                      onChange={(event) => setControls(event.target.value)}
                    />
                  </Field>
                  <Field label="Success metric">
                    <input
                      className="input"
                      required
                      value={metric}
                      onChange={(event) => setMetric(event.target.value)}
                    />
                  </Field>
                </div>
                <button
                  className="button-primary mt-5 w-full"
                  type="submit"
                  disabled={createExperiment.isPending}
                >
                  <Beaker className="size-4" />
                  Create controlled experiment
                </button>
                {createExperiment.isError && (
                  <p className="mt-3 text-xs text-danger">
                    {createExperiment.error.message}
                  </p>
                )}
              </form>
            </div>
          </section>

          <section className="surface p-5">
            <p className="eyebrow">Experiment ledger</p>
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {experiments.data?.map((experiment) => (
                <article key={experiment.id} className="rounded-xl border border-line p-4">
                  <div className="flex items-center justify-between">
                    <StatusPill tone="purple">{experiment.status}</StatusPill>
                    {experiment.is_demo && <StatusPill>Demo</StatusPill>}
                  </div>
                  <h3 className="mt-3 text-sm font-semibold">{experiment.title}</h3>
                  <p className="mt-2 text-xs leading-5 text-muted">{experiment.hypothesis}</p>
                  <p className="mt-3 text-[0.65rem] text-faint">
                    Variable: {experiment.variable} · metric: {experiment.success_metric}
                  </p>
                  <div className="mt-3 border-t border-line pt-3 text-[0.65rem] leading-5 text-faint">
                    Controls: {experiment.control_conditions.join(" · ")}
                  </div>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
}) {
  return (
    <div className="surface p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted">{label}</p>
        <Icon className="size-4 text-gold" />
      </div>
      <p className="mt-3 text-2xl font-semibold">{value.toLocaleString()}</p>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label>
      <span className="mb-2 block text-xs font-semibold text-muted">{label}</span>
      {children}
    </label>
  );
}
