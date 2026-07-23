"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BadgeCheck,
  BookOpenCheck,
  FileCheck2,
  FilePlus2,
  History,
  Lightbulb,
  ListChecks,
  PenLine,
  ShieldAlert,
  Sparkles,
  Timer,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { ContentBrief, Script } from "@/lib/contracts";

type DraftState = {
  body: string;
  hook: string;
  variants: string;
  cta: string;
  duration: string;
};

const emptyDraft: DraftState = {
  body: "",
  hook: "",
  variants: "",
  cta: "",
  duration: "60",
};

export default function StudioPage() {
  const queryClient = useQueryClient();
  const [selectedBriefId, setSelectedBriefId] = useState<string | null>(null);
  const [selectedScriptId, setSelectedScriptId] = useState<string | null>(null);
  const [draft, setDraft] = useState<DraftState>(emptyDraft);
  const [sourceUrls, setSourceUrls] = useState("");
  const [unresolvedClaims, setUnresolvedClaims] = useState("");

  const ideas = useQuery({ queryKey: ["ideas", "studio"], queryFn: () => api.ideas() });
  const briefs = useQuery({ queryKey: ["studio", "briefs"], queryFn: api.briefs });
  const scripts = useQuery({ queryKey: ["studio", "scripts"], queryFn: api.scripts });

  const refreshStudio = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["studio"] }),
      queryClient.invalidateQueries({ queryKey: ["ideas"] }),
      queryClient.invalidateQueries({ queryKey: ["content"] }),
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
      queryClient.invalidateQueries({ queryKey: ["approvals"] }),
    ]);
  };
  const createBrief = useMutation({
    mutationFn: (ideaId: string) =>
      api.createBriefFromIdea(ideaId, { platform: "LinkedIn", format: "Post" }),
    onSuccess: async (brief) => {
      setSelectedBriefId(brief.id);
      setDraft({
        body: brief.core_message,
        hook: `The system behind ${brief.title.toLowerCase()}.`,
        variants: "",
        cta: brief.cta,
        duration: String(brief.duration_seconds),
      });
      await refreshStudio();
    },
  });
  const saveScript = useMutation({
    mutationFn: ({
      brief,
      script,
      payload,
    }: {
      brief: ContentBrief;
      script: Script | null;
      payload: Parameters<typeof api.createScript>[1];
    }) =>
      script
        ? api.addScriptVersion(script.id, payload)
        : api.createScript(brief.id, payload),
    onSuccess: async (script) => {
      setSelectedScriptId(script.id);
      await refreshStudio();
    },
  });
  const factCheck = useMutation({
    mutationFn: ({
      script,
      sources,
      unresolved,
    }: {
      script: Script;
      sources: string[];
      unresolved: string[];
    }) =>
      api.factCheckScript(script.id, {
        claim_table: [],
        sources: sources.map((url) => ({ url, review: "manual" })),
        unresolved_claims: unresolved,
        verified_text: script.current_version?.body_text ?? "",
        confidence: unresolved.length ? 0.4 : 0.85,
      }),
    onSuccess: refreshStudio,
  });
  const submitScript = useMutation({
    mutationFn: api.submitScript,
    onSuccess: refreshStudio,
  });

  const ideaIdsWithBriefs = useMemo(
    () => new Set(briefs.data?.map((brief) => brief.idea_id) ?? []),
    [briefs.data],
  );
  const availableIdeas =
    ideas.data?.items.filter(
      (idea) =>
        !ideaIdsWithBriefs.has(idea.id) &&
        idea.status !== "rejected" &&
        idea.status !== "archived",
    ) ?? [];
  const selectedBrief =
    briefs.data?.find((brief) => brief.id === selectedBriefId) ??
    briefs.data?.[0] ??
    null;
  const scriptForBrief =
    scripts.data?.find((script) => script.content_brief_id === selectedBrief?.id) ?? null;
  const selectedScript =
    (selectedScriptId
      ? scripts.data?.find((script) => script.id === selectedScriptId)
      : scriptForBrief) ?? null;

  const openBrief = (brief: ContentBrief) => {
    setSelectedBriefId(brief.id);
    const script = scripts.data?.find((item) => item.content_brief_id === brief.id);
    setSelectedScriptId(script?.id ?? null);
    setDraft(
      script?.current_version
        ? {
            body: script.current_version.body_text,
            hook: script.current_version.hook_selected,
            variants: script.hooks
              .filter((hook) => !hook.is_recommended)
              .map((hook) => hook.text)
              .join("\n"),
            cta: script.current_version.cta,
            duration: String(script.current_version.duration_seconds),
          }
        : {
            body: brief.core_message,
            hook: `The system behind ${brief.title.toLowerCase()}.`,
            variants: "",
            cta: brief.cta,
            duration: String(brief.duration_seconds),
          },
    );
  };

  const submitDraft = (event: FormEvent) => {
    event.preventDefault();
    if (!selectedBrief || draft.body.trim().length < 20 || draft.hook.trim().length < 3) {
      return;
    }
    saveScript.mutate({
      brief: selectedBrief,
      script: scriptForBrief,
      payload: {
        body_text: draft.body.trim(),
        hook_selected: draft.hook.trim(),
        hook_variants: draft.variants
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
        cta: draft.cta.trim() || selectedBrief.cta,
        duration_seconds: Number(draft.duration) || selectedBrief.duration_seconds,
        brand_alignment_score: 8.5,
        originality_score: 8.5,
        change_summary: scriptForBrief ? "Studio revision" : "Initial studio draft",
      },
    });
  };

  const runFactCheck = () => {
    if (!selectedScript?.current_version) return;
    factCheck.mutate({
      script: selectedScript,
      sources: sourceUrls
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      unresolved: unresolvedClaims
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
    });
  };

  const loading = ideas.isPending || briefs.isPending || scripts.isPending;
  const error = ideas.error ?? briefs.error ?? scripts.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Brief Builder · Script Studio · Hook Lab"
        title="Turn possibility into an approved production asset."
        description="Ideas become structured briefs, scripts remain immutable by version, hooks carry explainable scores, factual and financial risks block approval, and only the backend can clear production."
        actions={
          <div className="flex gap-2">
            <StatusPill tone="blue">{briefs.data?.length ?? 0} briefs</StatusPill>
            <StatusPill tone="purple">{scripts.data?.length ?? 0} scripts</StatusPill>
          </div>
        }
      />

      {loading && <LoadingGrid />}
      {error && (
        <ErrorState
          error={error}
          retry={() => {
            void ideas.refetch();
            void briefs.refetch();
            void scripts.refetch();
          }}
        />
      )}

      {!loading && !error && (
        <>
          <section className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
            <div className="space-y-5">
              <div className="surface p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="eyebrow">Ideas ready to develop</p>
                    <h2 className="mt-2 text-lg font-semibold">Start with source intent</h2>
                  </div>
                  <Lightbulb className="size-5 text-gold" />
                </div>
                <div className="mt-5 space-y-3">
                  {availableIdeas.slice(0, 6).map((idea) => (
                    <article
                      key={idea.id}
                      className="rounded-xl border border-line bg-canvas/45 p-4"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold">{idea.title}</p>
                          <p className="mt-1 text-[0.65rem] text-faint">
                            {idea.pillar ?? "Unassigned"} · score{" "}
                            {idea.total_priority_score.toFixed(1)}
                          </p>
                        </div>
                        {idea.is_demo && <StatusPill>Demo</StatusPill>}
                      </div>
                      <p className="mt-3 line-clamp-3 text-xs leading-5 text-muted">
                        {idea.raw_input}
                      </p>
                      <button
                        className="button-secondary mt-4 w-full"
                        type="button"
                        disabled={createBrief.isPending}
                        onClick={() => createBrief.mutate(idea.id)}
                      >
                        <FilePlus2 className="size-4" />
                        Create structured brief
                      </button>
                    </article>
                  ))}
                  {availableIdeas.length === 0 && (
                    <p className="rounded-xl border border-dashed border-line p-4 text-xs text-muted">
                      Every current idea already has a brief. Capture another idea to continue.
                    </p>
                  )}
                </div>
              </div>

              <div className="surface p-5">
                <p className="eyebrow">Brief library</p>
                <div className="mt-4 space-y-2">
                  {briefs.data?.map((brief) => (
                    <button
                      key={brief.id}
                      type="button"
                      onClick={() => openBrief(brief)}
                      className={`focus-ring w-full rounded-xl border p-3 text-left transition ${
                        selectedBrief?.id === brief.id
                          ? "border-gold/35 bg-gold/7"
                          : "border-line bg-canvas/45 hover:border-line-bright"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-xs font-semibold">{brief.title}</p>
                        <StatusPill
                          tone={brief.evidence_status === "verified" ? "green" : "gold"}
                        >
                          {brief.evidence_status.replaceAll("_", " ")}
                        </StatusPill>
                      </div>
                      <p className="mt-2 text-[0.64rem] text-faint">
                        {brief.platform} · {brief.format} · {brief.pillar}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <form className="surface p-5 sm:p-6" onSubmit={submitDraft}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="eyebrow">Script editor</p>
                  <h2 className="mt-2 text-xl font-semibold">
                    {selectedBrief?.title ?? "Select a brief"}
                  </h2>
                </div>
                {scriptForBrief && (
                  <StatusPill tone="purple">
                    <History className="size-3" /> v{scriptForBrief.version_count}
                  </StatusPill>
                )}
              </div>
              {selectedBrief ? (
                <>
                  <div className="mt-5 grid gap-3 sm:grid-cols-3">
                    <BriefMetric label="Audience" value={selectedBrief.audience} />
                    <BriefMetric label="Emotion" value={selectedBrief.desired_emotion} />
                    <BriefMetric label="Success" value={selectedBrief.success_metric} />
                  </div>
                  <label className="mt-5 block">
                    <span className="mb-2 block text-xs font-semibold text-muted">
                      Selected hook
                    </span>
                    <input
                      className="input"
                      value={draft.hook}
                      onChange={(event) =>
                        setDraft((current) => ({ ...current, hook: event.target.value }))
                      }
                    />
                  </label>
                  <label className="mt-4 block">
                    <span className="mb-2 block text-xs font-semibold text-muted">
                      Hook variants · one per line
                    </span>
                    <textarea
                      className="input min-h-24 resize-y"
                      value={draft.variants}
                      onChange={(event) =>
                        setDraft((current) => ({ ...current, variants: event.target.value }))
                      }
                    />
                  </label>
                  <label className="mt-4 block">
                    <span className="mb-2 block text-xs font-semibold text-muted">
                      Script body
                    </span>
                    <textarea
                      className="input min-h-72 resize-y leading-6"
                      value={draft.body}
                      onChange={(event) =>
                        setDraft((current) => ({ ...current, body: event.target.value }))
                      }
                    />
                  </label>
                  <div className="mt-4 grid gap-4 sm:grid-cols-[1fr_9rem]">
                    <label>
                      <span className="mb-2 block text-xs font-semibold text-muted">CTA</span>
                      <input
                        className="input"
                        value={draft.cta}
                        onChange={(event) =>
                          setDraft((current) => ({ ...current, cta: event.target.value }))
                        }
                      />
                    </label>
                    <label>
                      <span className="mb-2 block text-xs font-semibold text-muted">
                        Duration
                      </span>
                      <input
                        className="input"
                        type="number"
                        min="10"
                        max="7200"
                        value={draft.duration}
                        onChange={(event) =>
                          setDraft((current) => ({
                            ...current,
                            duration: event.target.value,
                          }))
                        }
                      />
                    </label>
                  </div>
                  <button
                    className="button-primary mt-5 w-full"
                    type="submit"
                    disabled={
                      saveScript.isPending ||
                      draft.body.trim().length < 20 ||
                      draft.hook.trim().length < 3
                    }
                  >
                    <PenLine className="size-4" />
                    {scriptForBrief ? "Save immutable revision" : "Create first script version"}
                  </button>
                  {saveScript.isError && (
                    <p className="mt-4 text-xs text-danger">{saveScript.error.message}</p>
                  )}
                </>
              ) : (
                <div className="grid min-h-96 place-items-center text-center">
                  <div>
                    <FilePlus2 className="mx-auto size-8 text-gold" />
                    <p className="mt-4 text-sm text-muted">
                      Create or select a brief to open the editor.
                    </p>
                  </div>
                </div>
              )}
            </form>
          </section>

          <section className="grid gap-5 xl:grid-cols-[1fr_0.9fr]">
            <HookLab script={selectedScript} />
            <ReviewPanel
              script={selectedScript}
              sourceUrls={sourceUrls}
              setSourceUrls={setSourceUrls}
              unresolvedClaims={unresolvedClaims}
              setUnresolvedClaims={setUnresolvedClaims}
              checking={factCheck.isPending}
              checkError={factCheck.error}
              onReview={runFactCheck}
              submitting={submitScript.isPending}
              submitError={submitScript.error}
              onSubmit={() => selectedScript && submitScript.mutate(selectedScript.id)}
            />
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
      <p className="mt-1 line-clamp-2 text-xs font-semibold text-ink">{value}</p>
    </div>
  );
}

function HookLab({ script }: { script: Script | null }) {
  return (
    <div className="surface p-5 sm:p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Hook Lab</p>
          <h2 className="mt-2 text-xl font-semibold">Explainable openings</h2>
        </div>
        <Sparkles className="size-5 text-purple" />
      </div>
      <div className="mt-5 space-y-3">
        {script?.hooks.map((hook) => (
          <article key={hook.id} className="rounded-xl border border-line bg-canvas/45 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex gap-2">
                <StatusPill tone={hook.is_recommended ? "green" : "neutral"}>
                  {hook.is_recommended ? "recommended" : hook.category}
                </StatusPill>
              </div>
              <strong className="text-sm text-gold-bright">{hook.total_score.toFixed(1)}</strong>
            </div>
            <p className="mt-3 text-sm leading-6 text-ink">{hook.text}</p>
            <div className="mt-4 grid grid-cols-3 gap-2 text-[0.62rem] text-faint">
              <span>Clarity {hook.clarity_score.toFixed(1)}</span>
              <span>Brand {hook.brand_fit_score.toFixed(1)}</span>
              <span>Original {hook.originality_score.toFixed(1)}</span>
            </div>
          </article>
        ))}
        {!script && (
          <p className="rounded-xl border border-dashed border-line p-5 text-xs text-muted">
            Hook scores appear after a script version is saved.
          </p>
        )}
      </div>
    </div>
  );
}

function ReviewPanel({
  script,
  sourceUrls,
  setSourceUrls,
  unresolvedClaims,
  setUnresolvedClaims,
  checking,
  checkError,
  onReview,
  submitting,
  submitError,
  onSubmit,
}: {
  script: Script | null;
  sourceUrls: string;
  setSourceUrls: (value: string) => void;
  unresolvedClaims: string;
  setUnresolvedClaims: (value: string) => void;
  checking: boolean;
  checkError: Error | null;
  onReview: () => void;
  submitting: boolean;
  submitError: Error | null;
  onSubmit: () => void;
}) {
  return (
    <div className="surface p-5 sm:p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Evidence and approval</p>
          <h2 className="mt-2 text-xl font-semibold">Production gate</h2>
        </div>
        <StatusPill
          tone={
            script?.fact_check_status === "verified"
              ? "green"
              : script?.fact_check_status === "blocked"
                ? "danger"
                : "gold"
          }
        >
          {script?.fact_check_status.replaceAll("_", " ") ?? "no script"}
        </StatusPill>
      </div>
      {script ? (
        <>
          <div className="mt-5 grid grid-cols-2 gap-3">
            <BriefMetric label="Financial risk" value={script.financial_risk} />
            <BriefMetric label="Approval" value={script.approval_status} />
          </div>
          <label className="mt-5 block">
            <span className="mb-2 block text-xs font-semibold text-muted">
              Authoritative source URLs · one per line
            </span>
            <textarea
              className="input min-h-20 resize-y"
              value={sourceUrls}
              onChange={(event) => setSourceUrls(event.target.value)}
              placeholder="Leave empty only when the script makes no external factual claims."
            />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-xs font-semibold text-muted">
              Unresolved claims · one per line
            </span>
            <textarea
              className="input min-h-20 resize-y"
              value={unresolvedClaims}
              onChange={(event) => setUnresolvedClaims(event.target.value)}
              placeholder="Any entry blocks approval."
            />
          </label>
          <button
            className="button-secondary mt-4 w-full"
            type="button"
            disabled={checking || !script.current_version}
            onClick={onReview}
          >
            <ListChecks className="size-4" />
            {checking ? "Recording review…" : "Record manual fact and safety review"}
          </button>
          {checkError && <p className="mt-3 text-xs text-danger">{checkError.message}</p>}
          {script.fact_check && (
            <div
              className={`mt-4 rounded-xl border p-4 ${
                script.fact_check.status === "verified"
                  ? "border-green/20 bg-green/5"
                  : "border-danger/25 bg-danger/7"
              }`}
            >
              <div className="flex items-center gap-2 text-sm font-semibold">
                {script.fact_check.status === "verified" ? (
                  <BookOpenCheck className="size-4 text-green" />
                ) : (
                  <ShieldAlert className="size-4 text-danger" />
                )}
                {script.fact_check.financial_classification.replaceAll("_", " ")}
              </div>
              {script.fact_check.blocked_claims.map((claim) => (
                <p key={claim} className="mt-2 text-xs text-danger">
                  Blocked: {claim}
                </p>
              ))}
              {script.fact_check.risk_disclosures.map((disclosure) => (
                <p key={disclosure} className="mt-2 text-xs leading-5 text-muted">
                  {disclosure}
                </p>
              ))}
            </div>
          )}
          <button
            className="button-primary mt-4 w-full"
            type="button"
            disabled={
              submitting ||
              script.fact_check_status !== "verified" ||
              script.approval_status === "pending" ||
              script.approval_status === "approved"
            }
            onClick={onSubmit}
          >
            <FileCheck2 className="size-4" />
            {script.approval_status === "pending"
              ? "Waiting in Approval Queue"
              : script.approval_status === "approved"
                ? "Final script approved"
                : submitting
                  ? "Creating approval…"
                  : "Submit final script for approval"}
          </button>
          {submitError && <p className="mt-3 text-xs text-danger">{submitError.message}</p>}
          <p className="mt-4 flex items-start gap-2 text-[0.68rem] leading-5 text-faint">
            <BadgeCheck className="mt-0.5 size-3.5 shrink-0 text-gold" />
            Fact-check status is a recorded human assertion. Unsupported or unresolved claims
            must be entered above; prohibited financial language is blocked automatically.
          </p>
        </>
      ) : (
        <div className="grid min-h-72 place-items-center text-center">
          <div>
            <Timer className="mx-auto size-8 text-gold" />
            <p className="mt-4 text-sm text-muted">Save a script to open the review gate.</p>
          </div>
        </div>
      )}
    </div>
  );
}
