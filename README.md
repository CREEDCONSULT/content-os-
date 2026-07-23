# Mezie BrandOS

Mezie BrandOS is a local-first, AI-assisted brand engineering harness for operating the Mr. C. Mezie personal brand. It combines brand intelligence, idea capture, content production, governed memory, approvals, analytics, and proof of work in one premium command center.

> See the possibility. Build the system. Become the evidence.

## Current state

Development is active. The repository was created from an empty GitHub remote on
2026-07-23 and the original planning package is preserved under
[`docs/source`](docs/source).

The first connected implementation milestone includes:

- responsive Next.js command center and secure local login;
- FastAPI health/readiness, cookie auth, and typed API contracts;
- PostgreSQL schema, Alembic migration, deterministic seed, and Docker Compose;
- 52 imported Brand Intelligence records with immutable versions and provenance;
- live Ideas Inbox and governed 15-state content lifecycle;
- deterministic mock provider disclosure and server-side adapter status;
- backend-enforced approval records and negative transition tests;
- realistic August-December 2026 demo data, visibly labeled in the product.

See [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) for verified
status rather than intended scope.

## Repository layout

```text
apps/
  api/                 FastAPI modular monolith
  web/                 Next.js App Router frontend
docs/
  source/              preserved specifications and approved UI references
scripts/               development, bootstrap, and validation commands
```

## Local development

The canonical production-like local path is:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Then open `http://localhost:3100`. Port 3100 intentionally avoids the existing
Creed/Open WebUI service on port 3000. Local bootstrap credentials are documented in
`.env.example`; replace them before any remote exposure. Follow
[`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md) for host-mode commands
and verification.

## Safety

- Secrets stay in `.env` and are never committed.
- Public publishing, public scheduling, outreach, high-risk financial content, sensitive stories, canonical brand changes, and destructive deletion require backend approval.
- External integrations default to disabled or deterministic mocks.
- The existing `C:\CreedAI` installation is treated as an external dependency and is not modified by this repository.

## Source and decisions

- [`docs/SOURCE_DOCUMENT_INVENTORY.md`](docs/SOURCE_DOCUMENT_INVENTORY.md)
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)
- [`docs/RISK_REGISTER.md`](docs/RISK_REGISTER.md)
- [`docs/HUMAN_ACTION_QUEUE.md`](docs/HUMAN_ACTION_QUEUE.md)
