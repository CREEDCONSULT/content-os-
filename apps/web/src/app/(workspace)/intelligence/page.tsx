"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  BotMessageSquare,
  BrainCircuit,
  DatabaseBackup,
  Mic,
  Play,
  RefreshCw,
} from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";

export default function IntelligencePage() {
  const queryClient = useQueryClient();
  const runs = useQuery({ queryKey: ["heartbeat"], queryFn: api.heartbeatRuns });
  const memory = useQuery({ queryKey: ["memory"], queryFn: api.memoryRecords });
  const messages = useQuery({ queryKey: ["telegram"], queryFn: api.telegramMessages });
  const [capture, setCapture] = useState("");
  const [captureType, setCaptureType] = useState<"text" | "voice">("voice");
  const [syncResult, setSyncResult] = useState<string | null>(null);

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["heartbeat"] }),
      queryClient.invalidateQueries({ queryKey: ["memory"] }),
      queryClient.invalidateQueries({ queryKey: ["telegram"] }),
      queryClient.invalidateQueries({ queryKey: ["ideas"] }),
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
    ]);
  };
  const heartbeat = useMutation({ mutationFn: api.runHeartbeat, onSuccess: refresh });
  const sync = useMutation({
    mutationFn: api.syncVault,
    onSuccess: async (result) => {
      setSyncResult(
        `${result.exported} exported · ${result.imported} imported · ${result.conflicts} conflicts`,
      );
      await refresh();
    },
  });
  const telegram = useMutation({
    mutationFn: api.captureTelegramFixture,
    onSuccess: async () => {
      setCapture("");
      await refresh();
    },
  });

  const submitCapture = (event: FormEvent) => {
    event.preventDefault();
    telegram.mutate({
      sender_id: 0,
      message_type: captureType,
      ...(captureType === "voice" ? { transcript: capture } : { text: capture }),
    });
  };

  const latest = runs.data?.[0] ?? null;
  const loading = runs.isPending || memory.isPending || messages.isPending;
  const error = runs.error ?? memory.error ?? messages.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Daily intelligence · Memory · Telegram"
        title="Keep the brand current without letting automation outrun evidence."
        description="Manual heartbeat runs use canonical local context, stored benchmarks, and analytics. The vault sync preserves conflicts, and the Telegram fixture proves write-back without pretending a live bot is configured."
        actions={
          <button
            className="button-primary"
            type="button"
            disabled={heartbeat.isPending}
            onClick={() => heartbeat.mutate()}
          >
            <Play className="size-4" />
            Run daily intelligence
          </button>
        }
      />

      {loading && <LoadingGrid />}
      {error && <ErrorState error={error} retry={() => void refresh()} />}

      {!loading && !error && (
        <>
          <section className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
            <div className="surface p-5 sm:p-6">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="eyebrow">Latest daily brief</p>
                  <h2 className="mt-2 text-xl font-semibold">
                    {latest?.brief?.title ?? "No heartbeat brief yet"}
                  </h2>
                </div>
                {latest && (
                  <div className="flex gap-2">
                    <StatusPill tone={latest.status === "completed" ? "green" : "gold"}>
                      {latest.status}
                    </StatusPill>
                    {latest.is_demo && <StatusPill>Demo</StatusPill>}
                  </div>
                )}
              </div>
              {latest?.brief ? (
                <>
                  <div className="mt-5 grid gap-4 sm:grid-cols-3">
                    <BriefMetric
                      label="Context sources"
                      value={String(
                        Number(latest.source_coverage[0]?.records ?? 0),
                      )}
                    />
                    <BriefMetric
                      label="Opportunities"
                      value={String(latest.brief.content_opportunities.length)}
                    />
                    <BriefMetric
                      label="Cost"
                      value={`$${(latest.model_cost + latest.tool_cost).toFixed(2)}`}
                    />
                  </div>
                  <div className="mt-5 rounded-xl border border-gold/20 bg-gold/5 p-4">
                    <p className="text-[0.62rem] uppercase tracking-wider text-gold">
                      Priority recommendation
                    </p>
                    <p className="mt-2 text-sm leading-6 text-ink">
                      {latest.brief.recommended_action}
                    </p>
                  </div>
                  <div className="mt-5 grid gap-4 lg:grid-cols-2">
                    <div>
                      <p className="text-xs font-semibold text-muted">Content opportunities</p>
                      <div className="mt-3 space-y-2">
                        {latest.brief.content_opportunities.map((item, index) => (
                          <div
                            key={`${String(item.title)}-${index}`}
                            className="rounded-xl border border-line p-3"
                          >
                            <p className="text-xs font-semibold">{String(item.title)}</p>
                            <p className="mt-1 text-[0.65rem] text-faint">
                              {String(item.pillar ?? "Unassigned")} ·{" "}
                              {String(item.classification ?? "working")}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-muted">Coverage gaps</p>
                      <div className="mt-3 space-y-2">
                        {latest.brief.coverage_gaps.map((gap) => (
                          <div
                            key={gap}
                            className="flex gap-2 rounded-xl border border-gold/20 bg-gold/5 p-3 text-xs leading-5 text-gold-bright"
                          >
                            <AlertTriangle className="mt-0.5 size-4 shrink-0" />
                            {gap}
                          </div>
                        ))}
                        {latest.brief.coverage_gaps.length === 0 && (
                          <p className="rounded-xl border border-green/20 p-3 text-xs text-green">
                            No coverage gap was recorded.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="grid min-h-64 place-items-center text-center">
                  <div>
                    <Activity className="mx-auto size-8 text-gold" />
                    <p className="mt-3 text-sm text-muted">
                      Run the first deterministic intelligence cycle.
                    </p>
                  </div>
                </div>
              )}
              {heartbeat.isError && (
                <p className="mt-4 text-xs text-danger">{heartbeat.error.message}</p>
              )}
            </div>

            <div className="space-y-5">
              <div className="surface p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Dedicated vault</p>
                    <h2 className="mt-2 text-lg font-semibold">Database ↔ Markdown</h2>
                  </div>
                  <DatabaseBackup className="size-5 text-blue" />
                </div>
                <div className="mt-5 grid grid-cols-2 gap-3">
                  <BriefMetric label="Memory records" value={String(memory.data?.length ?? 0)} />
                  <BriefMetric
                    label="Conflicts"
                    value={String(
                      memory.data?.filter((item) => item.sync_status === "conflict").length ??
                        0,
                    )}
                  />
                </div>
                <button
                  className="button-secondary mt-4 w-full"
                  type="button"
                  disabled={sync.isPending}
                  onClick={() => sync.mutate()}
                >
                  <RefreshCw className={`size-4 ${sync.isPending ? "animate-spin" : ""}`} />
                  Synchronize vault
                </button>
                {syncResult && <p className="mt-3 text-xs text-green">{syncResult}</p>}
                {sync.isError && (
                  <p className="mt-3 text-xs text-danger">{sync.error.message}</p>
                )}
                <p className="mt-4 text-[0.68rem] leading-5 text-faint">
                  Canonical manual edits become conflicts and are never silently overwritten.
                  Embeddings remain disabled until a model alias is configured.
                </p>
              </div>

              <form className="surface p-5" onSubmit={submitCapture}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Telegram fixture</p>
                    <h2 className="mt-2 text-lg font-semibold">Test dashboard write-back</h2>
                  </div>
                  {captureType === "voice" ? (
                    <Mic className="size-5 text-purple" />
                  ) : (
                    <BotMessageSquare className="size-5 text-purple" />
                  )}
                </div>
                <div className="mt-4 flex gap-2">
                  {(["voice", "text"] as const).map((type) => (
                    <button
                      key={type}
                      className={captureType === type ? "button-primary" : "button-secondary"}
                      type="button"
                      onClick={() => setCaptureType(type)}
                    >
                      {type}
                    </button>
                  ))}
                </div>
                <textarea
                  className="input mt-4 min-h-28 resize-y"
                  required
                  minLength={3}
                  value={capture}
                  placeholder={
                    captureType === "voice"
                      ? "Paste a local transcription fixture…"
                      : "/idea A captured Telegram thought…"
                  }
                  onChange={(event) => setCapture(event.target.value)}
                />
                <button
                  className="button-secondary mt-4 w-full"
                  type="submit"
                  disabled={telegram.isPending || capture.trim().length < 3}
                >
                  <BrainCircuit className="size-4" />
                  Route fixture to BrandOS
                </button>
                {telegram.isError && (
                  <p className="mt-3 text-xs text-danger">{telegram.error.message}</p>
                )}
                <p className="mt-4 text-[0.68rem] leading-5 text-faint">
                  Simulator records carry a Demo badge. Live Telegram remains disabled until a
                  bot secret and sender allowlist are configured.
                </p>
              </form>
            </div>
          </section>

          <section className="surface p-5">
            <p className="eyebrow">Recent Telegram adapter records</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {messages.data?.slice(0, 6).map((message) => (
                <article key={message.id} className="rounded-xl border border-line p-4">
                  <div className="flex items-center justify-between">
                    <StatusPill tone={message.status === "completed" ? "green" : "gold"}>
                      {message.status.replaceAll("_", " ")}
                    </StatusPill>
                    {message.is_demo && <StatusPill>Demo fixture</StatusPill>}
                  </div>
                  <p className="mt-3 line-clamp-3 text-xs leading-5 text-muted">
                    {message.transcript ?? message.text ?? "No message content"}
                  </p>
                  <p className="mt-3 text-[0.65rem] leading-5 text-faint">
                    {message.response_text}
                  </p>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function BriefMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-line bg-canvas/45 p-3">
      <p className="text-[0.62rem] text-faint">{label}</p>
      <p className="mt-1 text-lg font-semibold text-ink">{value}</p>
    </div>
  );
}
