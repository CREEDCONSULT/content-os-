"use client";

import { useQuery } from "@tanstack/react-query";
import { BookMarked, ChevronRight, FileText, Search, ShieldCheck, X } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/page-header";
import { EmptyState, ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { BrandDocument } from "@/lib/contracts";

export default function BrandIntelligencePage() {
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const documents = useQuery({
    queryKey: ["brand-documents", search],
    queryFn: () => api.brandDocuments(search),
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Brand Intelligence"
        title="The governed source of brand truth."
        description="Canonical positioning, operating contracts, visual direction, execution systems, and the skill library—imported with provenance and immutable versions."
        actions={
          <div className="flex items-center gap-2 rounded-xl border border-green/25 bg-green/7 px-3 py-2 text-xs text-green">
            <ShieldCheck className="size-4" />
            Approval-gated canon
          </div>
        }
      />

      <div className="surface flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="relative block flex-1 sm:max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-faint" />
          <input
            className="input pl-10"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search the brand knowledge base…"
            aria-label="Search brand documents"
          />
        </label>
        <div className="flex items-center gap-4 text-xs text-muted">
          <span>
            <strong className="text-ink">{documents.data?.length ?? "—"}</strong> records
          </span>
          <span className="h-4 w-px bg-line" />
          <span>Source import · 2026</span>
        </div>
      </div>

      {documents.isPending && <LoadingGrid />}
      {documents.isError && (
        <ErrorState error={documents.error} retry={() => void documents.refetch()} />
      )}
      {documents.data?.length === 0 && (
        <EmptyState
          title="No brand records match this search."
          body="Clear the search or use a broader term. The underlying canon has not been changed."
        />
      )}

      {documents.data && documents.data.length > 0 && (
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {documents.data.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              onOpen={() => setSelectedId(document.id)}
            />
          ))}
        </section>
      )}

      {selectedId && <DocumentDrawer id={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  );
}

function DocumentCard({
  document,
  onOpen,
}: {
  document: BrandDocument;
  onOpen: () => void;
}) {
  const canonical = document.canonical_status === "canonical";
  return (
    <button
      type="button"
      onClick={onOpen}
      className="surface focus-ring group flex min-h-52 flex-col p-5 text-left transition hover:-translate-y-0.5 hover:border-gold/35"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="grid size-10 place-items-center rounded-xl border border-line bg-canvas/65">
          {document.document_type === "skill" ? (
            <BookMarked className="size-5 text-purple" />
          ) : (
            <FileText className="size-5 text-gold" />
          )}
        </div>
        <StatusPill tone={canonical ? "green" : "neutral"} dot={canonical}>
          {document.canonical_status}
        </StatusPill>
      </div>
      <p className="eyebrow mt-5">{document.document_type.replaceAll("-", " ")}</p>
      <h2 className="mt-2 line-clamp-2 text-base font-semibold leading-6">{document.title}</h2>
      <div className="mt-auto flex items-end justify-between gap-3 pt-5 text-[0.68rem] text-faint">
        <span>
          v{document.version_count} · {document.sensitivity}
        </span>
        <ChevronRight className="size-4 transition group-hover:translate-x-1 group-hover:text-gold" />
      </div>
    </button>
  );
}

function DocumentDrawer({ id, onClose }: { id: string; onClose: () => void }) {
  const detail = useQuery({
    queryKey: ["brand-document", id],
    queryFn: () => api.brandDocument(id),
  });

  return (
    <div className="fixed inset-0 z-[70] flex justify-end">
      <button
        type="button"
        aria-label="Close document detail"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      <aside className="relative h-full w-full overflow-y-auto border-l border-line bg-panel p-5 shadow-2xl sm:max-w-2xl sm:p-8">
        <div className="flex items-center justify-between">
          <BrandMark compact />
          <button className="button-ghost min-h-9 px-2" type="button" onClick={onClose}>
            <X className="size-5" />
            <span className="sr-only">Close</span>
          </button>
        </div>

        {detail.isPending && <div className="skeleton mt-10 h-72 rounded-2xl" />}
        {detail.isError && <ErrorState error={detail.error} retry={() => void detail.refetch()} />}
        {detail.data && (
          <article className="mt-8">
            <div className="flex flex-wrap gap-2">
              <StatusPill tone="green">{detail.data.canonical_status}</StatusPill>
              <StatusPill>v{detail.data.current_version?.version_number ?? 0}</StatusPill>
              <StatusPill>{detail.data.sensitivity}</StatusPill>
            </div>
            <p className="eyebrow mt-7">{detail.data.document_type.replaceAll("-", " ")}</p>
            <h1 className="mt-3 font-display text-3xl font-semibold leading-tight tracking-[-0.03em]">
              {detail.data.title}
            </h1>
            <div className="mt-6 grid gap-3 rounded-xl border border-line bg-canvas/45 p-4 text-xs text-muted sm:grid-cols-2">
              <div>
                <span className="block text-faint">Source</span>
                <span className="mt-1 block break-all">{detail.data.source_path ?? "Internal"}</span>
              </div>
              <div>
                <span className="block text-faint">Provenance</span>
                <span className="mt-1 block">
                  {detail.data.current_version?.created_by ?? "Unknown importer"}
                </span>
              </div>
            </div>
            <div className="mt-7 whitespace-pre-wrap rounded-xl border border-line bg-[#080b10] p-5 font-mono text-[0.76rem] leading-6 text-[#c4cad3]">
              {detail.data.current_version?.content_markdown ?? "No active content version."}
            </div>
          </article>
        )}
      </aside>
    </div>
  );
}

function BrandMark({ compact }: { compact: boolean }) {
  return (
    <div className="flex items-center gap-2 text-xs font-semibold text-muted">
      <BookMarked className="size-4 text-gold" />
      {compact && "Brand Intelligence record"}
    </div>
  );
}
