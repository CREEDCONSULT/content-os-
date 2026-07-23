"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpenCheck,
  ExternalLink,
  Plus,
  ShieldCheck,
  Sparkles,
  UsersRound,
} from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";

export default function BenchmarksPage() {
  const queryClient = useQueryClient();
  const creators = useQuery({ queryKey: ["intelligence", "creators"], queryFn: api.creators });
  const benchmarks = useQuery({
    queryKey: ["intelligence", "benchmarks"],
    queryFn: api.benchmarks,
  });
  const [creatorName, setCreatorName] = useState("");
  const [creatorUsername, setCreatorUsername] = useState("");
  const [creatorUrl, setCreatorUrl] = useState("");
  const [creatorPlatform, setCreatorPlatform] = useState("YouTube");
  const [creatorReason, setCreatorReason] = useState("");
  const [selectedCreator, setSelectedCreator] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [title, setTitle] = useState("");
  const [hook, setHook] = useState("");
  const [structure, setStructure] = useState("");
  const [mechanics, setMechanics] = useState("");
  const [excerpt, setExcerpt] = useState("");

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["intelligence"] });
  const addCreator = useMutation({
    mutationFn: api.createCreator,
    onSuccess: async (creator) => {
      setSelectedCreator(creator.id);
      setCreatorName("");
      setCreatorUsername("");
      setCreatorUrl("");
      setCreatorReason("");
      await refresh();
    },
  });
  const addBenchmark = useMutation({
    mutationFn: api.createBenchmark,
    onSuccess: async () => {
      setSourceUrl("");
      setTitle("");
      setHook("");
      setStructure("");
      setMechanics("");
      setExcerpt("");
      await refresh();
    },
  });

  const submitCreator = (event: FormEvent) => {
    event.preventDefault();
    addCreator.mutate({
      name: creatorName,
      username: creatorUsername,
      platform: creatorPlatform,
      url: creatorUrl,
      why_tracked: creatorReason,
      tier: 3,
      relevance_score: 7,
    });
  };

  const submitBenchmark = (event: FormEvent) => {
    event.preventDefault();
    addBenchmark.mutate({
      creator_id: selectedCreator || undefined,
      source_url: sourceUrl,
      title,
      transcript_excerpt: excerpt || undefined,
      observed_hook: hook,
      observed_structure: structure,
      transferable_mechanics: mechanics
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      pattern_tags: ["operator-supplied"],
    });
  };

  const loading = creators.isPending || benchmarks.isPending;
  const error = creators.error ?? benchmarks.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Creator intelligence · Transfer mechanics, never identity"
        title="Study what works without becoming a copy of who made it."
        description="The benchmark lab preserves source provenance, separates reusable mechanics from protected creator identity, and produces original Mezie adaptation prompts with explicit evidence limits."
        actions={<StatusPill tone="purple">{benchmarks.data?.length ?? 0} teardowns</StatusPill>}
      />

      {loading && <LoadingGrid />}
      {error && <ErrorState error={error} retry={() => void refresh()} />}

      {!loading && !error && (
        <>
          <section className="grid gap-5 xl:grid-cols-2">
            <form className="surface p-5" onSubmit={submitCreator}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Watchlist</p>
                  <h2 className="mt-2 text-lg font-semibold">Add a creator reference</h2>
                </div>
                <UsersRound className="size-5 text-blue" />
              </div>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <Field label="Display name">
                  <input
                    className="input"
                    required
                    minLength={2}
                    value={creatorName}
                    onChange={(event) => setCreatorName(event.target.value)}
                  />
                </Field>
                <Field label="Username">
                  <input
                    className="input"
                    required
                    minLength={2}
                    value={creatorUsername}
                    onChange={(event) => setCreatorUsername(event.target.value)}
                  />
                </Field>
                <Field label="Platform">
                  <select
                    className="input"
                    value={creatorPlatform}
                    onChange={(event) => setCreatorPlatform(event.target.value)}
                  >
                    {["YouTube", "Instagram", "TikTok", "LinkedIn", "X"].map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Profile URL">
                  <input
                    className="input"
                    required
                    type="url"
                    value={creatorUrl}
                    onChange={(event) => setCreatorUrl(event.target.value)}
                  />
                </Field>
              </div>
              <Field label="Why this creator is relevant" className="mt-4">
                <textarea
                  className="input min-h-24 resize-y"
                  required
                  minLength={3}
                  value={creatorReason}
                  onChange={(event) => setCreatorReason(event.target.value)}
                />
              </Field>
              <button
                className="button-secondary mt-5 w-full"
                type="submit"
                disabled={addCreator.isPending}
              >
                <Plus className="size-4" />
                Add to watchlist
              </button>
              {addCreator.isError && (
                <p className="mt-3 text-xs text-danger">{addCreator.error.message}</p>
              )}
            </form>

            <form className="surface p-5" onSubmit={submitBenchmark}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Content teardown</p>
                  <h2 className="mt-2 text-lg font-semibold">Analyze supplied evidence</h2>
                </div>
                <BookOpenCheck className="size-5 text-gold" />
              </div>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <Field label="Creator · optional">
                  <select
                    className="input"
                    value={selectedCreator}
                    onChange={(event) => setSelectedCreator(event.target.value)}
                  >
                    <option value="">Unlinked reference</option>
                    {creators.data?.map((creator) => (
                      <option key={creator.id} value={creator.id}>
                        {creator.name}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Source URL">
                  <input
                    className="input"
                    type="url"
                    required
                    value={sourceUrl}
                    onChange={(event) => setSourceUrl(event.target.value)}
                  />
                </Field>
              </div>
              <Field label="Reference title" className="mt-4">
                <input
                  className="input"
                  required
                  minLength={3}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                />
              </Field>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Field label="Observed hook">
                  <textarea
                    className="input min-h-24 resize-y"
                    required
                    value={hook}
                    onChange={(event) => setHook(event.target.value)}
                  />
                </Field>
                <Field label="Observed structure">
                  <textarea
                    className="input min-h-24 resize-y"
                    required
                    value={structure}
                    onChange={(event) => setStructure(event.target.value)}
                  />
                </Field>
              </div>
              <Field label="Transferable mechanics · one per line" className="mt-4">
                <textarea
                  className="input min-h-24 resize-y"
                  required
                  value={mechanics}
                  onChange={(event) => setMechanics(event.target.value)}
                />
              </Field>
              <Field label="Short transcript excerpt · optional" className="mt-4">
                <textarea
                  className="input min-h-20 resize-y"
                  value={excerpt}
                  onChange={(event) => setExcerpt(event.target.value)}
                />
              </Field>
              <button
                className="button-primary mt-5 w-full"
                type="submit"
                disabled={addBenchmark.isPending || !mechanics.trim()}
              >
                <Sparkles className="size-4" />
                Create governed teardown
              </button>
              {addBenchmark.isError && (
                <p className="mt-3 text-xs text-danger">{addBenchmark.error.message}</p>
              )}
            </form>
          </section>

          <section className="grid gap-5 lg:grid-cols-[0.65fr_1.35fr]">
            <div className="surface p-5">
              <p className="eyebrow">Active watchlist</p>
              <div className="mt-4 space-y-3">
                {creators.data?.map((creator) => (
                  <article key={creator.id} className="rounded-xl border border-line p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-semibold">{creator.name}</h3>
                        <p className="mt-1 text-[0.65rem] text-faint">
                          {creator.platform} · Tier {creator.tier} · relevance{" "}
                          {creator.relevance_score.toFixed(1)}
                        </p>
                      </div>
                      {creator.is_demo && <StatusPill>Demo</StatusPill>}
                    </div>
                    <p className="mt-3 text-xs leading-5 text-muted">{creator.why_tracked}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              {benchmarks.data?.map((benchmark) => (
                <article key={benchmark.id} className="surface p-5 sm:p-6">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap gap-2">
                        <StatusPill tone="blue">{benchmark.platform}</StatusPill>
                        <StatusPill tone="purple">{benchmark.evidence_level}</StatusPill>
                        {benchmark.is_demo && <StatusPill>Demo</StatusPill>}
                      </div>
                      <h2 className="mt-3 text-lg font-semibold">{benchmark.title}</h2>
                    </div>
                    <span className="text-faint" aria-label="Source preserved">
                      <ExternalLink className="size-5" />
                    </span>
                  </div>
                  <div className="mt-5 grid gap-4 sm:grid-cols-2">
                    <Analysis label="Hook" value={benchmark.hook_analysis} />
                    <Analysis label="Structure" value={benchmark.structure_analysis} />
                  </div>
                  <div className="mt-5 grid gap-4 lg:grid-cols-2">
                    <div className="rounded-xl border border-green/20 bg-green/5 p-4">
                      <p className="flex items-center gap-2 text-xs font-semibold text-green">
                        <Sparkles className="size-4" />
                        Transferable mechanics
                      </p>
                      <ul className="mt-3 space-y-2 text-xs leading-5 text-muted">
                        {benchmark.transferable_mechanics.map((item) => (
                          <li key={item}>• {item}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-xl border border-gold/20 bg-gold/5 p-4">
                      <p className="flex items-center gap-2 text-xs font-semibold text-gold">
                        <ShieldCheck className="size-4" />
                        Protected identity boundary
                      </p>
                      <ul className="mt-3 space-y-2 text-xs leading-5 text-muted">
                        {benchmark.protected_identity.map((item) => (
                          <li key={item}>• {item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="mt-4 rounded-xl border border-purple/20 bg-purple/5 p-4">
                    <p className="text-xs font-semibold text-purple">Original Mezie adaptations</p>
                    {benchmark.mezie_adaptations.map((item) => (
                      <p key={item} className="mt-2 text-xs leading-5 text-muted">
                        {item}
                      </p>
                    ))}
                  </div>
                  <div className="mt-4 border-t border-line pt-4 text-[0.68rem] leading-5 text-faint">
                    {benchmark.limitations.join(" · ")}
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

function Field({
  label,
  className = "",
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <label className={`block ${className}`}>
      <span className="mb-2 block text-xs font-semibold text-muted">{label}</span>
      {children}
    </label>
  );
}

function Analysis({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[0.62rem] uppercase tracking-wider text-faint">{label}</p>
      <p className="mt-2 text-xs leading-5 text-muted">{value}</p>
    </div>
  );
}
