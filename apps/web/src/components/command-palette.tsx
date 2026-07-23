"use client";

import { useQuery } from "@tanstack/react-query";
import { Command, Search, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";

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
                  authenticated records only
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
              {searchQuery.data?.length === 0 && (
                <p className="p-6 text-center text-sm text-muted">
                  No matching workspace records.
                </p>
              )}
              <div className="space-y-1">
                {searchQuery.data?.map((result) => (
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
