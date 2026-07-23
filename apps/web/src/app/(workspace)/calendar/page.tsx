"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, Gauge, Plus, ShieldAlert } from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { CalendarEvent } from "@/lib/contracts";

export default function CalendarPage() {
  const queryClient = useQueryClient();
  const capacities = useQuery({ queryKey: ["calendar", "capacity"], queryFn: api.capacities });
  const events = useQuery({ queryKey: ["calendar", "events"], queryFn: api.calendarEvents });
  const [weekStart, setWeekStart] = useState("2026-08-03");
  const [hours, setHours] = useState("10");
  const [maxShoots, setMaxShoots] = useState("2");
  const [maxEdits, setMaxEdits] = useState("3");
  const [fallback, setFallback] = useState(
    "Publish one verified low-production proof note if the planned shoot slips.",
  );
  const [title, setTitle] = useState("");
  const [eventType, setEventType] = useState<CalendarEvent["event_type"]>("shoot");
  const [startAt, setStartAt] = useState("2026-08-11T10:00");
  const [endAt, setEndAt] = useState("2026-08-11T11:30");
  const [units, setUnits] = useState("1.5");

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["calendar"] });
  const saveCapacity = useMutation({
    mutationFn: api.setCapacity,
    onSuccess: refresh,
  });
  const addEvent = useMutation({
    mutationFn: api.createCalendarEvent,
    onSuccess: async () => {
      setTitle("");
      await refresh();
    },
  });

  const submitCapacity = (event: FormEvent) => {
    event.preventDefault();
    saveCapacity.mutate({
      week_start: weekStart,
      available_hours: Number(hours),
      max_shoots: Number(maxShoots),
      max_edits: Number(maxEdits),
      fallback_plan: fallback,
    });
  };

  const submitEvent = (event: FormEvent) => {
    event.preventDefault();
    addEvent.mutate({
      title,
      event_type: eventType,
      start_at: new Date(startAt).toISOString(),
      end_at: new Date(endAt).toISOString(),
      capacity_units: Number(units),
    });
  };

  const loading = capacities.isPending || events.isPending;
  const error = capacities.error ?? events.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Calendar orchestration · Capacity first"
        title="Commit to a rhythm the team can actually sustain."
        description="Every scheduled block consumes explicit weekly capacity. Shoots and edits are capped, and each week carries a fallback plan instead of an invisible promise."
        actions={<StatusPill tone="blue">{events.data?.length ?? 0} scheduled</StatusPill>}
      />

      {loading && <LoadingGrid />}
      {error && <ErrorState error={error} retry={() => void refresh()} />}

      {!loading && !error && (
        <>
          <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
            <form className="surface p-5" onSubmit={submitCapacity}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Weekly capacity</p>
                  <h2 className="mt-2 text-lg font-semibold">Set the operating envelope</h2>
                </div>
                <Gauge className="size-5 text-gold" />
              </div>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <Field label="Week of">
                  <input
                    className="input"
                    type="date"
                    value={weekStart}
                    onChange={(event) => setWeekStart(event.target.value)}
                  />
                </Field>
                <Field label="Available hours">
                  <input
                    className="input"
                    type="number"
                    min="1"
                    value={hours}
                    onChange={(event) => setHours(event.target.value)}
                  />
                </Field>
                <Field label="Maximum shoots">
                  <input
                    className="input"
                    type="number"
                    min="0"
                    value={maxShoots}
                    onChange={(event) => setMaxShoots(event.target.value)}
                  />
                </Field>
                <Field label="Maximum edits">
                  <input
                    className="input"
                    type="number"
                    min="0"
                    value={maxEdits}
                    onChange={(event) => setMaxEdits(event.target.value)}
                  />
                </Field>
              </div>
              <Field label="Fallback if the plan slips" className="mt-4">
                <textarea
                  className="input min-h-24 resize-y"
                  value={fallback}
                  onChange={(event) => setFallback(event.target.value)}
                />
              </Field>
              <button
                className="button-primary mt-5 w-full"
                type="submit"
                disabled={saveCapacity.isPending}
              >
                <Gauge className="size-4" />
                Save capacity plan
              </button>
              {saveCapacity.isError && (
                <p className="mt-3 text-xs text-danger">{saveCapacity.error.message}</p>
              )}
            </form>

            <form className="surface p-5" onSubmit={submitEvent}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Schedule work</p>
                  <h2 className="mt-2 text-lg font-semibold">Reserve a real production block</h2>
                </div>
                <CalendarClock className="size-5 text-blue" />
              </div>
              <Field label="Title" className="mt-5">
                <input
                  className="input"
                  required
                  minLength={3}
                  value={title}
                  placeholder="Founder shoot · BrandOS evidence"
                  onChange={(event) => setTitle(event.target.value)}
                />
              </Field>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Field label="Work type">
                  <select
                    className="input"
                    value={eventType}
                    onChange={(event) =>
                      setEventType(event.target.value as CalendarEvent["event_type"])
                    }
                  >
                    {["research", "write", "review", "shoot", "edit", "editorial_publish"].map(
                      (value) => (
                        <option key={value} value={value}>
                          {value.replaceAll("_", " ")}
                        </option>
                      ),
                    )}
                  </select>
                </Field>
                <Field label="Capacity hours">
                  <input
                    className="input"
                    type="number"
                    min="0.25"
                    step="0.25"
                    value={units}
                    onChange={(event) => setUnits(event.target.value)}
                  />
                </Field>
                <Field label="Starts">
                  <input
                    className="input"
                    type="datetime-local"
                    value={startAt}
                    onChange={(event) => setStartAt(event.target.value)}
                  />
                </Field>
                <Field label="Ends">
                  <input
                    className="input"
                    type="datetime-local"
                    value={endAt}
                    onChange={(event) => setEndAt(event.target.value)}
                  />
                </Field>
              </div>
              <button
                className="button-secondary mt-5 w-full"
                type="submit"
                disabled={addEvent.isPending || title.trim().length < 3}
              >
                <Plus className="size-4" />
                Add to calendar
              </button>
              {addEvent.isError && (
                <div className="mt-3 flex items-start gap-2 text-xs text-danger">
                  <ShieldAlert className="mt-0.5 size-4 shrink-0" />
                  {addEvent.error.message}
                </div>
              )}
            </form>
          </section>

          <section className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
            <div className="surface p-5">
              <p className="eyebrow">Capacity ledger</p>
              <div className="mt-4 space-y-3">
                {capacities.data?.map((capacity) => (
                  <article key={capacity.id} className="rounded-xl border border-line p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold">
                          Week of {formatDate(capacity.week_start)}
                        </p>
                        <p className="mt-1 text-xs text-muted">
                          {capacity.available_hours}h · {capacity.max_shoots} shoots ·{" "}
                          {capacity.max_edits} edits
                        </p>
                      </div>
                      {capacity.is_demo && <StatusPill>Demo</StatusPill>}
                    </div>
                    <p className="mt-3 text-xs leading-5 text-faint">{capacity.fallback_plan}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="surface p-5">
              <p className="eyebrow">Scheduled commitments</p>
              <div className="mt-4 divide-y divide-line">
                {events.data?.map((item) => (
                  <article key={item.id} className="flex gap-4 py-4 first:pt-0">
                    <div className="w-14 shrink-0 rounded-xl border border-line bg-canvas/55 p-2 text-center">
                      <p className="text-[0.62rem] uppercase text-faint">
                        {new Date(item.start_at).toLocaleDateString("en-CA", { month: "short" })}
                      </p>
                      <p className="mt-1 text-lg font-semibold">
                        {new Date(item.start_at).getDate()}
                      </p>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-sm font-semibold">{item.title}</h3>
                        <StatusPill tone={item.event_type === "shoot" ? "purple" : "blue"}>
                          {item.event_type.replaceAll("_", " ")}
                        </StatusPill>
                        {item.is_demo && <StatusPill>Demo</StatusPill>}
                      </div>
                      <p className="mt-2 text-xs text-muted">
                        {new Date(item.start_at).toLocaleString()} · {item.capacity_units}h
                      </p>
                    </div>
                  </article>
                ))}
              </div>
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

function formatDate(value: string) {
  return new Date(`${value}T12:00:00`).toLocaleDateString("en-CA", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
