"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CalendarClock, CircleDot, LockKeyhole, RefreshCw } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { ContentItem, PipelineGroup } from "@/lib/contracts";
import { compactGroup, NEXT_STATUS, PIPELINE_LABELS } from "@/lib/pipeline";

const groups: { id: PipelineGroup; label: string; detail: string }[] = [
  { id: "ideation", label: "Ideation", detail: "Idea → research → brief" },
  { id: "scripting", label: "Scripting", detail: "Script → review → approved" },
  { id: "production", label: "Production", detail: "Ready → shot → editing" },
  { id: "review", label: "Review", detail: "Edit review → publish-ready" },
  { id: "published", label: "Published", detail: "Learn → repurpose → archive" },
];

export default function PipelinePage() {
  const queryClient = useQueryClient();
  const [transitionError, setTransitionError] = useState("");
  const content = useQuery({
    queryKey: ["content"],
    queryFn: api.content,
  });
  const transition = useMutation({
    mutationFn: ({ id, toStatus }: { id: string; toStatus: ContentItem["status"] }) =>
      api.transitionContent(id, toStatus),
    onSuccess: async () => {
      setTransitionError("");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["content"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        queryClient.invalidateQueries({ queryKey: ["approvals"] }),
      ]);
    },
    onError: (error) => setTransitionError(error.message),
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Content Lifecycle"
        title="Fifteen states. One accountable flow."
        description="The interface groups work into five operational lanes while the backend preserves every stage, validates transitions, and gates publishing behind approval."
        actions={
          <div className="flex items-center gap-2 rounded-xl border border-gold/25 bg-gold/7 px-3 py-2 text-xs text-gold-bright">
            <LockKeyhole className="size-4" />
            Publish gate enforced
          </div>
        }
      />

      {transitionError && (
        <div className="flex items-start justify-between gap-4 rounded-xl border border-danger/25 bg-danger/8 p-4 text-sm text-danger">
          <span>{transitionError}</span>
          <button type="button" onClick={() => setTransitionError("")} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}

      {content.isPending && <LoadingGrid />}
      {content.isError && <ErrorState error={content.error} retry={() => void content.refetch()} />}
      {content.data?.items.length === 0 && (
        <EmptyState
          title="The lifecycle is ready for its first content item."
          body="Convert a selected idea into content to begin the governed production flow."
        />
      )}

      {content.data && content.data.items.length > 0 && (
        <>
          <section className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            {groups.map((group) => (
              <div key={group.id} className="rounded-xl border border-line bg-panel p-4">
                <p className="text-xs font-semibold text-muted">{group.label}</p>
                <strong className="mt-2 block font-display text-3xl">
                  {content.data.groups[group.id] ?? 0}
                </strong>
                <p className="mt-1 text-[0.62rem] leading-4 text-faint">{group.detail}</p>
              </div>
            ))}
          </section>

          <section className="overflow-x-auto pb-3">
            <div className="grid min-w-[78rem] grid-cols-5 gap-4">
              {groups.map((group) => {
                const items = content.data.items.filter(
                  (item) => compactGroup(item.status) === group.id,
                );
                return (
                  <div key={group.id} className="rounded-2xl border border-line bg-panel/50 p-3">
                    <div className="flex items-center justify-between px-1 py-2">
                      <div>
                        <p className="eyebrow">{group.label}</p>
                        <p className="mt-1 text-[0.66rem] text-faint">{group.detail}</p>
                      </div>
                      <span className="grid size-7 place-items-center rounded-full border border-line bg-canvas text-xs text-muted">
                        {items.length}
                      </span>
                    </div>
                    <div className="mt-3 space-y-3">
                      {items.length === 0 && (
                        <div className="rounded-xl border border-dashed border-line p-6 text-center text-xs text-faint">
                          No active item
                        </div>
                      )}
                      {items.map((item) => (
                        <ContentCard
                          key={item.id}
                          item={item}
                          moving={transition.isPending && transition.variables?.id === item.id}
                          onAdvance={() => {
                            const next = NEXT_STATUS[item.status];
                            if (next) transition.mutate({ id: item.id, toStatus: next });
                          }}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function ContentCard({
  item,
  moving,
  onAdvance,
}: {
  item: ContentItem;
  moving: boolean;
  onAdvance: () => void;
}) {
  const next = NEXT_STATUS[item.status];
  const approvalTone =
    item.approval_status === "approved"
      ? "green"
      : item.approval_status === "pending"
        ? "gold"
        : item.approval_status === "rejected"
          ? "danger"
          : "neutral";

  return (
    <article className="rounded-xl border border-line bg-panel-raised p-4 shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <StatusPill tone="blue">{PIPELINE_LABELS[item.status]}</StatusPill>
        {item.is_demo && <StatusPill>Demo</StatusPill>}
      </div>
      <h2 className="mt-4 text-sm font-semibold leading-5">{item.title}</h2>
      <p className="mt-2 text-xs text-muted">
        {item.platform} · {item.format} · {item.pillar}
      </p>
      <div className="mt-4 flex items-center justify-between gap-3 border-t border-line pt-3">
        <span className="flex items-center gap-1.5 text-[0.66rem] text-faint">
          <CalendarClock className="size-3.5" />
          {item.due_date ?? "Unscheduled"}
        </span>
        <StatusPill tone={approvalTone}>{item.approval_status.replaceAll("_", " ")}</StatusPill>
      </div>
      {item.blocker && (
        <p className="mt-3 rounded-lg border border-danger/20 bg-danger/5 p-2.5 text-[0.68rem] leading-4 text-danger">
          {item.blocker}
        </p>
      )}
      {next ? (
        <button
          className="button-secondary mt-4 w-full min-h-9 text-[0.7rem]"
          type="button"
          disabled={moving}
          onClick={onAdvance}
        >
          {moving ? <RefreshCw className="size-3.5 animate-spin" /> : <ArrowRight className="size-3.5" />}
          {moving ? "Moving…" : `Advance to ${PIPELINE_LABELS[next]}`}
        </button>
      ) : (
        <div className="mt-4 flex items-center gap-2 text-[0.7rem] text-faint">
          <CircleDot className="size-3.5" />
          Terminal lifecycle state
        </div>
      )}
    </article>
  );
}
