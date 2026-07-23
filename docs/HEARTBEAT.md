# Daily Intelligence Heartbeat

Last verified: 2026-07-23

The heartbeat creates at most one durable run and one brief per brand and date.
Repeated manual, scheduled, or retried calls return the existing run.

Each run records trigger, context pack, source coverage, model alias, tools, costs,
records changed, errors, confidence, and completion time. The brief separates
verified local changes, creator watch, working trend hypotheses, content
opportunities, risks/noise, recommendations, and coverage gaps.

External acquisition is not called while Apify is disabled. Such a brief becomes
`partial`, has zero external cost, and explicitly says it cannot make freshness or
performance claims.

## Execution

- Dashboard: `POST /api/v1/heartbeat/run`
- One-shot CLI: `scripts/run-heartbeat.ps1`
- Durable scheduler: Compose service `heartbeat`

The scheduler checks database settings every 60 seconds, honors the configured
IANA timezone and hour, and uses a date-based idempotency key. Scheduling is
disabled by default. Enabling it never enables publishing or external messaging.

Completed briefs synchronize into
`05_Research/Daily Intelligence/YYYY-MM-DD.md`.
