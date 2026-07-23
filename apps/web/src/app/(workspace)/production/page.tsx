"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Camera,
  Check,
  CircleAlert,
  Clapperboard,
  ListChecks,
  MapPin,
  Plus,
  Video,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { ProductionPlan } from "@/lib/contracts";

export default function ProductionPage() {
  const queryClient = useQueryClient();
  const plans = useQuery({ queryKey: ["production", "plans"], queryFn: api.productionPlans });
  const scripts = useQuery({ queryKey: ["studio", "scripts"], queryFn: api.scripts });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [location, setLocation] = useState("");
  const [scheduledAt, setScheduledAt] = useState("2026-08-11T10:00");

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["production"] }),
      queryClient.invalidateQueries({ queryKey: ["content"] }),
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
    ]);
  };
  const createPlan = useMutation({
    mutationFn: api.createProductionPlan,
    onSuccess: async (plan) => {
      setSelectedId(plan.id);
      setLocation(plan.location ?? "");
      await refresh();
    },
  });
  const updatePlan = useMutation({
    mutationFn: ({
      planId,
      nextLocation,
      nextScheduledAt,
    }: {
      planId: string;
      nextLocation: string;
      nextScheduledAt: string;
    }) =>
      api.updateProductionPlan(planId, {
        location: nextLocation,
        scheduled_at: new Date(nextScheduledAt).toISOString(),
      }),
    onSuccess: refresh,
  });
  const toggleChecklist = useMutation({
    mutationFn: ({ itemId, complete }: { itemId: string; complete: boolean }) =>
      api.setChecklistItem(itemId, complete),
    onSuccess: refresh,
  });

  const plan = plans.data?.find((item) => item.id === selectedId) ?? plans.data?.[0] ?? null;
  const plannedScriptIds = useMemo(
    () => new Set(plans.data?.map((item) => item.script_id) ?? []),
    [plans.data],
  );
  const eligibleScripts =
    scripts.data?.filter(
      (script) =>
        script.status === "approved" &&
        script.approval_status === "approved" &&
        !plannedScriptIds.has(script.id),
    ) ?? [];

  const selectPlan = (next: ProductionPlan) => {
    setSelectedId(next.id);
    setLocation(next.location ?? "");
    setScheduledAt(
      next.scheduled_at
        ? new Date(next.scheduled_at).toISOString().slice(0, 16)
        : "2026-08-11T10:00",
    );
  };

  const saveLogistics = (event: FormEvent) => {
    event.preventDefault();
    if (!plan) return;
    updatePlan.mutate({
      planId: plan.id,
      nextLocation: location,
      nextScheduledAt: scheduledAt,
    });
  };

  const loading = plans.isPending || scripts.isPending;
  const error = plans.error ?? scripts.error;

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Production planning · Mobile shoot mode"
        title="Nothing is ready until every blocker is visible."
        description="Approved scripts become scenes, shots, logistics, and checklists. BrandOS computes readiness on the server and advances the content lifecycle only at a genuine 100%."
        actions={
          plan ? (
            <StatusPill tone={plan.status === "ready" ? "green" : "gold"}>
              {plan.readiness_score.toFixed(0)}% ready
            </StatusPill>
          ) : undefined
        }
      />

      {loading && <LoadingGrid />}
      {error && <ErrorState error={error} retry={() => void refresh()} />}

      {!loading && !error && (
        <section className="grid gap-5 xl:grid-cols-[19rem_minmax(0,1fr)]">
          <aside className="space-y-5">
            <div className="surface p-4">
              <p className="eyebrow">Approved scripts</p>
              <div className="mt-4 space-y-2">
                {eligibleScripts.map((script) => (
                  <article key={script.id} className="rounded-xl border border-line p-3">
                    <p className="text-xs font-semibold">{script.title}</p>
                    <button
                      className="button-secondary mt-3 w-full"
                      type="button"
                      disabled={createPlan.isPending}
                      onClick={() => createPlan.mutate(script.id)}
                    >
                      <Plus className="size-4" />
                      Build plan
                    </button>
                  </article>
                ))}
                {eligibleScripts.length === 0 && (
                  <p className="rounded-xl border border-dashed border-line p-3 text-xs leading-5 text-muted">
                    No approved script is waiting for a plan. Approve a verified final version
                    in Script Studio first.
                  </p>
                )}
                {createPlan.isError && (
                  <p className="text-xs text-danger">{createPlan.error.message}</p>
                )}
              </div>
            </div>

            <div className="surface p-4">
              <p className="eyebrow">Production plans</p>
              <div className="mt-4 space-y-2">
                {plans.data?.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => selectPlan(item)}
                    className={`focus-ring w-full rounded-xl border p-3 text-left ${
                      plan?.id === item.id
                        ? "border-gold/35 bg-gold/7"
                        : "border-line bg-canvas/45"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-semibold">{item.title}</p>
                      {item.is_demo && <StatusPill>Demo</StatusPill>}
                    </div>
                    <p className="mt-2 text-[0.64rem] text-faint">
                      {item.status} · {item.readiness_score.toFixed(0)}%
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </aside>

          {plan ? (
            <div className="space-y-5">
              <section className="surface overflow-hidden">
                <div className="border-b border-line bg-gradient-to-r from-gold/10 to-transparent p-5 sm:p-6">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="eyebrow">Shoot command</p>
                      <h2 className="mt-2 text-2xl font-semibold">{plan.title}</h2>
                      <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
                        {plan.creative_treatment}
                      </p>
                    </div>
                    <div className="min-w-28 rounded-xl border border-line bg-canvas/65 p-4 text-center">
                      <p className="text-3xl font-semibold text-gold-bright">
                        {plan.readiness_score.toFixed(0)}
                      </p>
                      <p className="mt-1 text-[0.62rem] uppercase tracking-wider text-faint">
                        readiness
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid gap-5 p-5 sm:p-6 lg:grid-cols-[0.8fr_1.2fr]">
                  <form onSubmit={saveLogistics}>
                    <div className="flex items-center gap-2">
                      <MapPin className="size-4 text-blue" />
                      <h3 className="text-sm font-semibold">Logistics</h3>
                    </div>
                    <label className="mt-4 block">
                      <span className="mb-2 block text-xs text-muted">Location</span>
                      <input
                        className="input"
                        value={location}
                        placeholder={plan.location ?? "Confirm a quiet shoot location"}
                        onChange={(event) => setLocation(event.target.value)}
                      />
                    </label>
                    <label className="mt-4 block">
                      <span className="mb-2 block text-xs text-muted">Shoot time</span>
                      <input
                        className="input"
                        type="datetime-local"
                        value={scheduledAt}
                        onChange={(event) => setScheduledAt(event.target.value)}
                      />
                    </label>
                    <button
                      className="button-secondary mt-4 w-full"
                      type="submit"
                      disabled={updatePlan.isPending || !location.trim()}
                    >
                      Save logistics
                    </button>
                    {updatePlan.isError && (
                      <p className="mt-3 text-xs text-danger">{updatePlan.error.message}</p>
                    )}
                  </form>

                  <div>
                    <div className="flex items-center gap-2">
                      <CircleAlert className="size-4 text-gold" />
                      <h3 className="text-sm font-semibold">Active blockers</h3>
                    </div>
                    <div className="mt-4 space-y-2">
                      {plan.blockers.map((blocker) => (
                        <div
                          key={blocker}
                          className="rounded-xl border border-gold/20 bg-gold/5 p-3 text-xs text-gold-bright"
                        >
                          {blocker}
                        </div>
                      ))}
                      {plan.blockers.length === 0 && (
                        <div className="rounded-xl border border-green/20 bg-green/5 p-3 text-xs text-green">
                          All production gates passed. Content is ready to shoot.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </section>

              <section className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
                <div className="surface p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="eyebrow">Shoot checklist</p>
                      <h2 className="mt-2 text-lg font-semibold">Tap as you prepare</h2>
                    </div>
                    <ListChecks className="size-5 text-green" />
                  </div>
                  <div className="mt-5 space-y-3">
                    {plan.checklist.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        disabled={toggleChecklist.isPending}
                        onClick={() =>
                          toggleChecklist.mutate({
                            itemId: item.id,
                            complete: !item.is_complete,
                          })
                        }
                        className="focus-ring flex min-h-14 w-full items-center gap-3 rounded-xl border border-line bg-canvas/45 p-3 text-left"
                      >
                        <span
                          className={`grid size-7 shrink-0 place-items-center rounded-lg border ${
                            item.is_complete
                              ? "border-green/30 bg-green/15 text-green"
                              : "border-line-bright text-faint"
                          }`}
                        >
                          {item.is_complete && <Check className="size-4" />}
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block text-xs font-semibold">{item.label}</span>
                          <span className="mt-1 block text-[0.62rem] uppercase tracking-wide text-faint">
                            {item.phase.replaceAll("_", " ")}
                            {item.is_critical ? " · critical" : ""}
                          </span>
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="surface p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="eyebrow">Scene and shot list</p>
                      <h2 className="mt-2 text-lg font-semibold">Shoot in sequence</h2>
                    </div>
                    <Clapperboard className="size-5 text-purple" />
                  </div>
                  <div className="mt-5 space-y-4">
                    {plan.scenes.map((scene) => (
                      <article key={scene.id} className="rounded-xl border border-line p-4">
                        <div className="flex items-start gap-3">
                          <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-purple/10 text-xs font-bold text-purple">
                            {scene.sequence}
                          </span>
                          <div>
                            <h3 className="text-sm font-semibold">{scene.title}</h3>
                            <p className="mt-1 text-xs leading-5 text-muted">{scene.purpose}</p>
                          </div>
                        </div>
                        <blockquote className="mt-4 border-l-2 border-gold/40 pl-3 text-xs leading-5 text-ink">
                          {scene.dialogue}
                        </blockquote>
                        <div className="mt-4 grid gap-2 sm:grid-cols-2">
                          {plan.shots
                            .filter((shot) => shot.production_scene_id === scene.id)
                            .map((shot) => (
                              <div
                                key={shot.id}
                                className="rounded-lg border border-line bg-canvas/45 p-3"
                              >
                                <div className="flex items-center gap-2">
                                  {shot.is_b_roll ? (
                                    <Video className="size-3.5 text-blue" />
                                  ) : (
                                    <Camera className="size-3.5 text-gold" />
                                  )}
                                  <p className="text-[0.68rem] font-semibold">
                                    {shot.framing}
                                  </p>
                                </div>
                                <p className="mt-2 text-[0.65rem] leading-4 text-faint">
                                  {shot.camera_angle} · {shot.movement}
                                </p>
                                <p className="mt-2 text-[0.68rem] leading-5 text-muted">
                                  {shot.instructions}
                                </p>
                              </div>
                            ))}
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              </section>
            </div>
          ) : (
            <div className="surface grid min-h-96 place-items-center p-8 text-center">
              <div>
                <Clapperboard className="mx-auto size-9 text-gold" />
                <h2 className="mt-4 text-lg font-semibold">No production plan selected</h2>
                <p className="mt-2 text-sm text-muted">
                  Approve a verified script, then build its governed shoot plan.
                </p>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
