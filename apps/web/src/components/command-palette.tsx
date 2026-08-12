"use client";

import { useQuery } from "@tanstack/react-query";
import { Command, Search, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { GlobalSearchResult } from "@/lib/contracts";

const routeResults: GlobalSearchResult[] = [
  {
    id: "route-dashboard",
    record_type: "route",
    title: "Command center",
    excerpt: "Dashboard overview, operating posture, recent activity, and next work.",
    href: "/dashboard",
    authority: "navigation",
    score: 6,
    is_demo: false,
  },
  {
    id: "route-agent",
    record_type: "route",
    title: "Agent console",
    excerpt: "Run the Brand Director and inspect routed skills, sources, and proposals.",
    href: "/agent",
    authority: "navigation",
    score: 6,
    is_demo: false,
  },
  {
    id: "route-actions",
    record_type: "route",
    title: "Action inbox",
    excerpt: "Review, execute, or approval-gate agent-proposed dashboard actions.",
    href: "/actions",
    authority: "navigation",
    score: 6,
    is_demo: false,
  },
  {
    id: "route-approvals",
    record_type: "route",
    title: "Approval queue",
    excerpt: "Decide high-impact actions before public, paid, or sensitive execution.",
    href: "/approvals",
    authority: "navigation",
    score: 6,
    is_demo: false,
  },
  {
    id: "route-calendar",
    record_type: "route",
    title: "Content calendar",
    excerpt: "Plan internal production blocks, capacity, and rollout cadence.",
    href: "/calendar",
    authority: "navigation",
    score: 5,
    is_demo: false,
  },
  {
    id: "route-benchmarks",
    record_type: "route",
    title: "Creator benchmarks",
    excerpt: "Study creator mechanics without copying protected expression or identity.",
    href: "/benchmarks",
    authority: "navigation",
    score: 5,
    is_demo: false,
  },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const normalizedQuery = query.trim();
  const searchQuery = useQuery({
    queryKey: ["global-search", normalizedQuery],
    queryFn: () => api.search(normalizedQuery),
    enabled: open && normalizedQuery.length >= 2,
    staleTime: 15_000,
  });
  const visibleResults =
    normalizedQuery.length >= 2
      ? [
          ...routeResults
            .filter((route) =>
              `${route.title} ${route.excerpt} ${route.href}`
                .toLowerCase()
                .includes(normalizedQuery.toLowerCase()),
            )
            .map((route) => ({
              ...route,
              score: route.score + (route.title.toLowerCase().startsWith(normalizedQuery.toLowerCase()) ? 4 : 0),
            })),
          ...(searchQuery.data ?? []),
        ].sort((a, b) => b.score - a.score)
      : [];

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((current) => !current);
      }
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <>
      <button
        type="button"
        className="button-ghost min-h-9 gap-2 px-2 sm:px-3"
        onClick={() => setOpen(true)}
        aria-label="Search workspace"
      >
        <Search className="size-4" />
        <span className="hidden text-xs sm:inline">Search</span>
        <kbd className="hidden rounded border border-line px-1.5 py-0.5 text-[0.6rem] text-faint md:inline">
          Ctrl K
        </kbd>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-[80] flex items-start justify-center px-4 pt-[12vh]"
          role="dialog"
          aria-modal="true"
          aria-labelledby="command-palette-title"
        >
          <button
            type="button"
            className="absolute inset-0 bg-black/75 backdrop-blur-sm"
            aria-label="Close workspace search"
            onClick={() => setOpen(false)}
          />
          <div className="surface relative w-full max-w-2xl overflow-hidden p-0 shadow-2xl">
            <div className="flex items-center gap-3 border-b border-line px-4">
              <Search className="size-5 text-gold" />
              <label className="sr-only" htmlFor="global-search">
                Search workspace
              </label>
              <input
                id="global-search"
                autoFocus
                className="min-h-16 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-faint"
                placeholder="Search ideas, content, memory, creators…"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <button
                type="button"
                className="button-ghost min-h-9 px-2"
                onClick={() => setOpen(false)}
              >
                <X className="size-4" />
                <span className="sr-only">Close</span>
              </button>
            </div>

            <div className="max-h-[55vh] overflow-y-auto p-3">
              <div className="mb-2 flex items-center justify-between px-2">
                <p id="command-palette-title" className="eyebrow">
                  Workspace search
                </p>
                <span className="text-[0.65rem] text-faint">
                  <Command className="mr-1 inline size-3" />
                  routes + authenticated records
                </span>
              </div>

              {normalizedQuery.length < 2 && (
                <p className="p-6 text-center text-sm text-muted">
                  Type at least two characters to search the command center.
                </p>
              )}
              {searchQuery.isPending && normalizedQuery.length >= 2 && (
                <p className="p-6 text-center text-sm text-muted" role="status">
                  Searching…
                </p>
              )}
              {searchQuery.isError && (
                <p className="m-2 rounded-lg border border-danger/25 bg-danger/8 p-3 text-sm text-danger">
                  {searchQuery.error.message}
                </p>
              )}
              {visibleResults.length === 0 && normalizedQuery.length >= 2 && !searchQuery.isPending && (
                <p className="p-6 text-center text-sm text-muted">
                  No matching workspace records.
                </p>
              )}
              <div className="space-y-1">
                {visibleResults.map((result) => (
                  <Link
                    key={`${result.record_type}-${result.id}`}
                    href={result.href}
                    onClick={() => setOpen(false)}
                    className="focus-ring block rounded-xl border border-transparent p-3 transition hover:border-line hover:bg-panel"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-ink">
                          {result.title}
                        </p>
                        <p className="mt-1 line-clamp-2 text-xs leading-5 text-muted">
                          {result.excerpt}
                        </p>
                      </div>
                      <div className="flex shrink-0 flex-col items-end gap-1">
                        <span className="rounded-full border border-line px-2 py-1 text-[0.6rem] uppercase tracking-wide text-faint">
                          {result.record_type.replaceAll("_", " ")}
                        </span>
                        {result.is_demo && (
                          <span className="text-[0.6rem] font-semibold uppercase text-purple">
                            Demo
                          </span>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
