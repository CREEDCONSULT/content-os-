"use client";

import { useQuery } from "@tanstack/react-query";
import { Filter, Lightbulb, Plus, Search, Sparkles } from "lucide-react";
import { useState } from "react";

import { IdeaCaptureForm } from "@/components/idea-capture-form";
import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { Idea, IdeaStatus } from "@/lib/contracts";

const statuses: { value: "" | IdeaStatus; label: string }[] = [
  { value: "", label: "All states" },
  { value: "captured", label: "Captured" },
  { value: "clarifying", label: "Clarifying" },
  { value: "researching", label: "Researching" },
  { value: "selected", label: "Selected" },
  { value: "rejected", label: "Rejected" },
];

export default function IdeasPage() {
  const [captureOpen, setCaptureOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<"" | IdeaStatus>("");
  const ideas = useQuery({
    queryKey: ["ideas", search, status],
    queryFn: () => api.ideas(search, status),
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Idea Intelligence"
        title="Capture broadly. Select with evidence."
        description="Every possibility becomes a traceable object with brand fit, audience value, proof, timeliness, originality, feasibility, and strategic importance."
        actions={
          <button className="button-primary w-fit" type="button" onClick={() => setCaptureOpen(true)}>
            <Plus className="size-4" />
            Capture idea
          </button>
        }
      />

      <div className="surface grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_13rem_auto] md:items-center">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-faint" />
          <input
            className="input pl-10"
            placeholder="Search captured possibilities…"
            aria-label="Search ideas"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <label className="relative block">
          <Filter className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-faint" />
          <select
            className="input pl-10"
            value={status}
            onChange={(event) => setStatus(event.target.value as "" | IdeaStatus)}
            aria-label="Filter ideas by status"
          >
            {statuses.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <div className="text-right text-xs text-muted">
          <strong className="text-ink">{ideas.data?.total ?? "—"}</strong> idea records
        </div>
      </div>

      {ideas.isPending && <LoadingGrid />}
      {ideas.isError && <ErrorState error={ideas.error} retry={() => void ideas.refetch()} />}
      {ideas.data?.items.length === 0 && (
        <EmptyState
          title="No ideas match this view."
          body="Capture a possibility or adjust the current search and lifecycle filter."
        />
      )}

      {ideas.data && ideas.data.items.length > 0 && (
        <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
          {ideas.data.items.map((idea) => (
            <IdeaCard key={idea.id} idea={idea} />
          ))}
        </section>
      )}

      <IdeaCaptureForm open={captureOpen} onClose={() => setCaptureOpen(false)} />
    </div>
  );
}

function IdeaCard({ idea }: { idea: Idea }) {
  const statusTone =
    idea.status === "selected"
      ? "green"
      : idea.status === "rejected"
        ? "danger"
        : idea.status === "researching"
          ? "purple"
          : "blue";
  const score = idea.total_priority_score;
  const scoreDegrees = Math.min(360, Math.max(0, score * 36));

  return (
    <article className="surface flex min-h-72 flex-col p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          <StatusPill tone={statusTone}>{idea.status}</StatusPill>
          {idea.is_demo && <StatusPill>Demo</StatusPill>}
        </div>
        <div
          className="grid size-12 shrink-0 place-items-center rounded-full"
          style={{
            background: `radial-gradient(circle at center, #111722 57%, transparent 59%), conic-gradient(#d6ad5c ${scoreDegrees}deg, #263141 ${scoreDegrees}deg)`,
          }}
          aria-label={`Priority score ${score.toFixed(1)} out of 10`}
        >
          <span className="text-xs font-bold text-gold-bright">{score.toFixed(1)}</span>
        </div>
      </div>
      <p className="eyebrow mt-5">{idea.pillar ?? "Unassigned pillar"}</p>
      <h2 className="mt-2 text-lg font-semibold leading-6">{idea.title}</h2>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-muted">{idea.raw_input}</p>
      <div className="mt-5 flex flex-wrap gap-1.5">
        {idea.platform_fit.map((platform) => (
          <span
            key={platform}
            className="rounded-md border border-line bg-canvas/55 px-2 py-1 text-[0.65rem] text-muted"
          >
            {platform}
          </span>
        ))}
      </div>
      <div className="mt-auto flex items-center justify-between border-t border-line pt-4 text-xs text-faint">
        <span>{idea.series ?? idea.audience}</span>
        <span className="flex items-center gap-1 text-purple">
          {score > 0 ? <Sparkles className="size-3.5" /> : <Lightbulb className="size-3.5" />}
          {score > 0 ? "Scored" : "Awaiting score"}
        </span>
      </div>
    </article>
  );
}
