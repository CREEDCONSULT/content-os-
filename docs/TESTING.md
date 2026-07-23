# Testing

## Complete local gate

```powershell
npm run check
docker compose config --quiet
docker compose exec api .venv/bin/alembic check
.\scripts\security-check.ps1
.\scripts\test-backup-restore.ps1
```

`npm run check` runs:

- ESLint for Next.js.
- Ruff for FastAPI.
- TypeScript `tsc --noEmit`.
- Vitest component and domain tests.
- pytest API, policy, persistence, and integration tests.
- Next.js production build.

## High-value negative coverage

- protected routes reject anonymous access;
- invalid lifecycle/canonical/publishing transitions do not pass;
- financial claims and incomplete fact checks block script submission;
- capacity conflicts fail;
- production readiness cannot be spoofed below 100%;
- asset uploads enforce rights, size, name, hash, and deduplication;
- proof requires evidence and permission;
- vault conflicts preserve both sides and restricted memory stays out of context;
- Telegram rejects invalid secrets/senders and deduplicates updates;
- heartbeat runs deduplicate by date;
- benchmark adaptations enforce originality;
- CSV imports retain valid rows and report invalid rows;
- global search requires auth and a bounded query;
- offline replay removes only successfully persisted ideas.

## Browser and accessibility evidence

The connected flows were manually exercised at desktop and a 390-pixel mobile
viewport with no warning/error console entries. The shell uses landmark
navigation, labeled controls, visible focus styles, status live regions,
keyboard command search, escape-to-close behavior, and responsive reflow.

Automated assistive-technology/browser performance audits are not claimed in this
environment. They remain a public-release gate alongside real-device install,
offline, screen-reader, keyboard-only, and Core Web Vitals checks.

## Adding tests

- API tests belong in `apps/api/tests` and use the isolated SQLite fixture unless
  PostgreSQL behavior is the subject.
- Web tests belong beside the component or library and run in jsdom.
- A schema change requires forward migration, downgrade, re-upgrade, and
  `alembic check`.
- A destructive or externally visible action requires negative authorization and
  idempotency coverage before implementation is considered complete.
