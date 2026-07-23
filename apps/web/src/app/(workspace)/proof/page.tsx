"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Award, ExternalLink, FileWarning, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";

const initialNarrative = {
  title: "",
  credibilityGap: "",
  context: "",
  constraints: "",
  process: "",
  output: "",
  result: "",
  lessons: "",
  evidenceLabel: "",
  evidenceUrl: "",
};

export default function ProofPage() {
  const queryClient = useQueryClient();
  const proof = useQuery({ queryKey: ["proof"], queryFn: api.proofItems });
  const [form, setForm] = useState(initialNarrative);
  const [sensitivity, setSensitivity] = useState("internal");
  const [permission, setPermission] = useState("not_required");

  const create = useMutation({
    mutationFn: api.createProofItem,
    onSuccess: async () => {
      setForm(initialNarrative);
      await queryClient.invalidateQueries({ queryKey: ["proof"] });
    },
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const evidence =
      form.evidenceUrl.trim() && form.evidenceLabel.trim()
        ? [{ label: form.evidenceLabel.trim(), url: form.evidenceUrl.trim() }]
        : [];
    create.mutate({
      title: form.title,
      proof_type: "build_log",
      credibility_gap: form.credibilityGap,
      context: form.context,
      constraints: form.constraints,
      process: form.process,
      output: form.output,
      result: form.result,
      lessons: form.lessons,
      evidence_links: evidence,
      sensitivity,
      permission_status: permission,
    });
  };

  const set = (field: keyof typeof initialNarrative, value: string) =>
    setForm((current) => ({ ...current, [field]: value }));

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Proof of work · Evidence before claims"
        title="Turn completed work into credible, permission-aware evidence."
        description="A proof record separates context, constraints, process, output, result, and lessons. It remains evidence-needed until a real reference exists, and confidential client work stays gated by permission."
        actions={
          <StatusPill tone="green">
            {proof.data?.filter((item) => item.status === "verified").length ?? 0} verified
          </StatusPill>
        }
      />

      {proof.isPending && <LoadingGrid />}
      {proof.error && <ErrorState error={proof.error} retry={() => void proof.refetch()} />}

      {!proof.isPending && !proof.error && (
        <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
          <form className="surface h-fit p-5 sm:p-6" onSubmit={submit}>
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow">Capture proof</p>
                <h2 className="mt-2 text-lg font-semibold">Build an evidence narrative</h2>
              </div>
              <Award className="size-5 text-gold" />
            </div>
            <ProofField
              label="Proof title"
              value={form.title}
              onChange={(value) => set("title", value)}
            />
            <ProofField
              label="Credibility gap"
              value={form.credibilityGap}
              onChange={(value) => set("credibilityGap", value)}
            />
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {(
                [
                  ["context", "Context"],
                  ["constraints", "Constraints"],
                  ["process", "Process"],
                  ["output", "Output"],
                  ["result", "Result"],
                  ["lessons", "Lessons"],
                ] as [keyof typeof initialNarrative, string][]
              ).map(([field, label]) => (
                <ProofField
                  key={field}
                  label={label}
                  value={form[field]}
                  onChange={(value) => set(field, value)}
                  area
                />
              ))}
            </div>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <ProofField
                label="Evidence label"
                value={form.evidenceLabel}
                onChange={(value) => set("evidenceLabel", value)}
                optional
              />
              <ProofField
                label="Evidence URL or local reference"
                value={form.evidenceUrl}
                onChange={(value) => set("evidenceUrl", value)}
                optional
              />
              <label>
                <span className="mb-2 block text-xs font-semibold text-muted">Sensitivity</span>
                <select
                  className="input"
                  value={sensitivity}
                  onChange={(event) => {
                    setSensitivity(event.target.value);
                    if (event.target.value === "client_confidential") {
                      setPermission("pending");
                    }
                  }}
                >
                  <option value="internal">Internal</option>
                  <option value="public">Public</option>
                  <option value="client_confidential">Client confidential</option>
                </select>
              </label>
              <label>
                <span className="mb-2 block text-xs font-semibold text-muted">
                  Permission
                </span>
                <select
                  className="input"
                  value={permission}
                  onChange={(event) => setPermission(event.target.value)}
                >
                  <option value="not_required">Not required</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="denied">Denied</option>
                </select>
              </label>
            </div>
            <button
              className="button-primary mt-5 w-full"
              type="submit"
              disabled={
                create.isPending ||
                Object.entries(form)
                  .filter(([key]) => !key.startsWith("evidence"))
                  .some(([, value]) => value.trim().length < 3)
              }
            >
              <ShieldCheck className="size-4" />
              Record proof state
            </button>
            {create.isError && (
              <p className="mt-3 text-xs text-danger">{create.error.message}</p>
            )}
          </form>

          <div className="space-y-4">
            {proof.data?.map((item) => (
              <article key={item.id} className="surface p-5 sm:p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap gap-2">
                      <StatusPill
                        tone={item.status === "verified" ? "green" : "gold"}
                      >
                        {item.status.replaceAll("_", " ")}
                      </StatusPill>
                      <StatusPill tone="blue">{item.proof_type.replaceAll("_", " ")}</StatusPill>
                      {item.is_demo && <StatusPill>Demo</StatusPill>}
                    </div>
                    <h2 className="mt-3 text-lg font-semibold">{item.title}</h2>
                  </div>
                  {item.status === "verified" ? (
                    <ShieldCheck className="size-5 text-green" />
                  ) : (
                    <FileWarning className="size-5 text-gold" />
                  )}
                </div>
                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <ProofBlock label="Credibility gap" value={item.credibility_gap} />
                  <ProofBlock label="Context" value={item.context} />
                  <ProofBlock label="Constraints" value={item.constraints} />
                  <ProofBlock label="Process" value={item.process} />
                  <ProofBlock label="Output" value={item.output} />
                  <ProofBlock label="Result" value={item.result} />
                </div>
                <div className="mt-4 rounded-xl border border-line bg-canvas/45 p-4">
                  <p className="text-[0.62rem] uppercase tracking-wider text-faint">Lessons</p>
                  <p className="mt-2 text-xs leading-5 text-muted">{item.lessons}</p>
                </div>
                <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-line pt-4 text-xs">
                  <span className="text-faint">
                    {item.sensitivity.replaceAll("_", " ")} · permission{" "}
                    {item.permission_status.replaceAll("_", " ")}
                  </span>
                  {item.evidence_links.map((link, index) => (
                    <span
                      key={`${link.url ?? "evidence"}-${index}`}
                      className="inline-flex items-center gap-1.5 text-blue"
                    >
                      <ExternalLink className="size-3.5" />
                      {link.label ?? link.url ?? "Evidence"}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function ProofField({
  label,
  value,
  onChange,
  area = false,
  optional = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  area?: boolean;
  optional?: boolean;
}) {
  return (
    <label className="mt-4 block">
      <span className="mb-2 block text-xs font-semibold text-muted">
        {label}
        {optional ? " · optional" : ""}
      </span>
      {area ? (
        <textarea
          className="input min-h-24 resize-y"
          required={!optional}
          minLength={optional ? undefined : 3}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      ) : (
        <input
          className="input"
          required={!optional}
          minLength={optional ? undefined : 3}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      )}
    </label>
  );
}

function ProofBlock({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[0.62rem] uppercase tracking-wider text-faint">{label}</p>
      <p className="mt-2 text-xs leading-5 text-muted">{value}</p>
    </div>
  );
}
