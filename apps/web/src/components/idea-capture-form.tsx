"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Lightbulb, Plus, X } from "lucide-react";
import { FormEvent, useState } from "react";
import { z } from "zod";

import { api } from "@/lib/api";
import { cn } from "@/lib/cn";

export const ideaCaptureSchema = z.object({
  title: z.string().trim().min(3, "Give the idea a clear title."),
  raw_input: z.string().trim().min(3, "Capture the underlying thought or evidence."),
  pillar: z.string().optional(),
  audience: z.string().trim().min(2, "Name the primary audience."),
  platform_fit: z.array(z.string()).max(8),
});

const pillars = ["See", "Build", "Lead", "Own", "Leverage"];
const platforms = ["Instagram", "LinkedIn", "TikTok", "YouTube", "X"];

export function IdeaCaptureForm({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [rawInput, setRawInput] = useState("");
  const [pillar, setPillar] = useState("Build");
  const [audience, setAudience] = useState("Emerging Builder");
  const [platformFit, setPlatformFit] = useState<string[]>(["LinkedIn"]);
  const [validationError, setValidationError] = useState("");
  const [captureNotice, setCaptureNotice] = useState("");
  const createIdea = useMutation({
    mutationFn: api.createIdeaOrQueue,
    onSuccess: async (result) => {
      if (result.mode === "created") {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["ideas"] }),
          queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        ]);
      }
      setCaptureNotice(
        result.mode === "queued"
          ? "Saved on this device. BrandOS will replay it when the API reconnects."
          : "",
      );
      setTitle("");
      setRawInput("");
      setValidationError("");
      if (result.mode === "created") onClose();
    },
  });

  if (!open) return null;

  const togglePlatform = (platform: string) => {
    setPlatformFit((current) =>
      current.includes(platform)
        ? current.filter((item) => item !== platform)
        : [...current, platform],
    );
  };

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = ideaCaptureSchema.safeParse({
      title,
      raw_input: rawInput,
      pillar,
      audience,
      platform_fit: platformFit,
    });
    if (!parsed.success) {
      setValidationError(parsed.error.issues[0]?.message ?? "Review the idea fields.");
      return;
    }
    setValidationError("");
    setCaptureNotice("");
    createIdea.mutate(parsed.data);
  };

  return (
    <div className="fixed inset-0 z-[70] flex items-end justify-center sm:items-center sm:p-6">
      <button
        type="button"
        className="absolute inset-0 bg-black/75 backdrop-blur-sm"
        onClick={onClose}
        aria-label="Close idea capture"
      />
      <form
        className="surface relative max-h-[95vh] w-full overflow-y-auto rounded-b-none p-5 sm:max-w-2xl sm:rounded-2xl sm:p-7"
        onSubmit={onSubmit}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Fast capture</p>
            <h2 className="mt-2 font-display text-3xl font-semibold">Hold onto the possibility.</h2>
            <p className="mt-2 text-sm text-muted">
              This creates a real workspace record. Scoring and research remain separate decisions.
            </p>
          </div>
          <button className="button-ghost min-h-9 px-2" type="button" onClick={onClose}>
            <X className="size-5" />
            <span className="sr-only">Close</span>
          </button>
        </div>

        <div className="mt-7 grid gap-5 sm:grid-cols-2">
          <label className="block sm:col-span-2">
            <span className="mb-2 block text-xs font-semibold text-muted">Working title</span>
            <input
              className="input"
              placeholder="What is the idea?"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              autoFocus
            />
          </label>
          <label className="block sm:col-span-2">
            <span className="mb-2 block text-xs font-semibold text-muted">
              Raw thought, observation, or evidence
            </span>
            <textarea
              className="input min-h-28 resize-y"
              placeholder="Capture enough context for your future self and the intelligence layer…"
              value={rawInput}
              onChange={(event) => setRawInput(event.target.value)}
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-semibold text-muted">Brand pillar</span>
            <select className="input" value={pillar} onChange={(event) => setPillar(event.target.value)}>
              {pillars.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-semibold text-muted">Primary audience</span>
            <input
              className="input"
              value={audience}
              onChange={(event) => setAudience(event.target.value)}
            />
          </label>
        </div>

        <fieldset className="mt-5">
          <legend className="text-xs font-semibold text-muted">Platform fit</legend>
          <div className="mt-2 flex flex-wrap gap-2">
            {platforms.map((platform) => {
              const selected = platformFit.includes(platform);
              return (
                <button
                  key={platform}
                  type="button"
                  onClick={() => togglePlatform(platform)}
                  className={cn(
                    "focus-ring inline-flex items-center gap-1.5 rounded-full border px-3 py-2 text-xs font-semibold",
                    selected
                      ? "border-gold/40 bg-gold/10 text-gold-bright"
                      : "border-line bg-canvas/55 text-muted",
                  )}
                  aria-pressed={selected}
                >
                  {selected && <Check className="size-3.5" />}
                  {platform}
                </button>
              );
            })}
          </div>
        </fieldset>

        {captureNotice && (
          <p
            className="mt-5 rounded-lg border border-gold/25 bg-gold/8 p-3 text-xs text-gold-bright"
            role="status"
          >
            {captureNotice}
          </p>
        )}

        {(validationError || createIdea.isError) && (
          <p className="mt-5 rounded-lg border border-danger/25 bg-danger/8 p-3 text-xs text-danger">
            {validationError || createIdea.error?.message}
          </p>
        )}

        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button className="button-ghost" type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="button-primary" type="submit" disabled={createIdea.isPending}>
            {createIdea.isPending ? (
              <>
                <Lightbulb className="size-4 animate-pulse" />
                Capturing…
              </>
            ) : (
              <>
                <Plus className="size-4" />
                Capture idea
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
