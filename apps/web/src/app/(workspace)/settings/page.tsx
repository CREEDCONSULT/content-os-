"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Bot,
  CheckCircle2,
  CircleSlash2,
  CloudCog,
  Database,
  ExternalLink,
  KeyRound,
  LockKeyhole,
  MessageCircle,
} from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { ErrorState, LoadingGrid } from "@/components/query-state";
import { StatusPill } from "@/components/status-pill";
import { api } from "@/lib/api";
import type { Integration } from "@/lib/contracts";

const adapterIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  openai: Bot,
  telegram: MessageCircle,
  apify: CloudCog,
  "creed-memory": Database,
  vault: LockKeyhole,
};

const productionChecks = [
  "Rotate local auth password and session secret",
  "Enable secure cookies behind HTTPS",
  "Provision PostgreSQL and durable object storage",
  "Configure provider aliases and budget ceilings",
  "Verify Telegram allowlist before enabling capture",
  "Approve exact Apify Actors before any spend",
];

export default function SettingsPage() {
  const integrations = useQuery({
    queryKey: ["integrations"],
    queryFn: api.integrations,
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="System & Adapters"
        title="Real state, clearly disclosed."
        description="Connector status is derived server-side. Secrets are never returned to the browser, and unconfigured services remain disabled or deterministic mocks."
        actions={
          <StatusPill tone="green" dot>
            Server-side secrets
          </StatusPill>
        }
      />

      {integrations.isPending && <LoadingGrid />}
      {integrations.isError && (
        <ErrorState error={integrations.error} retry={() => void integrations.refetch()} />
      )}
      {integrations.data && (
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {integrations.data.items.map((integration) => (
            <AdapterCard key={integration.id} integration={integration} />
          ))}
        </section>
      )}

      <section className="grid gap-5 xl:grid-cols-[1fr_0.8fr]">
        <div className="surface p-5 sm:p-6">
          <p className="eyebrow">Production gate</p>
          <h2 className="mt-2 text-xl font-semibold">Before this leaves a local machine</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {productionChecks.map((check) => (
              <div key={check} className="flex gap-3 rounded-xl border border-line bg-canvas/45 p-4">
                <CircleSlash2 className="mt-0.5 size-4 shrink-0 text-gold" />
                <p className="text-xs leading-5 text-muted">{check}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="surface p-5 sm:p-6">
          <p className="eyebrow">Security posture</p>
          <h2 className="mt-2 text-xl font-semibold">Bootstrap, not public-ready</h2>
          <div className="mt-6 space-y-4">
            <div className="rounded-xl border border-green/20 bg-green/5 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-green">
                <CheckCircle2 className="size-4" />
                Enforced now
              </div>
              <p className="mt-2 text-xs leading-5 text-muted">
                HttpOnly sessions, CORS allowlist, backend approvals, immutable brand versions,
                validated lifecycle transitions, audit events, and no browser-exposed secrets.
              </p>
            </div>
            <div className="rounded-xl border border-gold/20 bg-gold/5 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-gold-bright">
                <KeyRound className="size-4" />
                Human action required
              </div>
              <p className="mt-2 text-xs leading-5 text-muted">
                Deployment credentials, domains, provider keys, final visual assets, and live
                connector decisions remain deliberately outside source control.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function AdapterCard({ integration }: { integration: Integration }) {
  const Icon = adapterIcons[integration.id] ?? ExternalLink;
  const tone =
    integration.state === "configured"
      ? "green"
      : integration.state === "mock"
        ? "purple"
        : integration.state === "error"
          ? "danger"
          : "neutral";

  return (
    <article className="surface min-h-44 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="grid size-10 place-items-center rounded-xl border border-line bg-canvas/55">
          <Icon className="size-5 text-gold" />
        </div>
        <StatusPill tone={tone} dot={integration.state === "configured"}>
          {integration.state}
        </StatusPill>
      </div>
      <h2 className="mt-5 text-base font-semibold">{integration.label}</h2>
      <p className="mt-2 text-xs leading-5 text-muted">{integration.detail}</p>
      <p className="mt-4 text-[0.64rem] text-faint">
        {integration.server_side_only ? "Server boundary" : "Public client"} · checked{" "}
        {new Date(integration.last_checked_at).toLocaleTimeString("en-CA", {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </p>
    </article>
  );
}
