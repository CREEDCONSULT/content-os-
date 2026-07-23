# Architecture

## Confirmed topology

Mezie BrandOS is a modular monolith with explicit module boundaries.

```text
Next.js installable PWA
      |
      | authenticated REST
      v
FastAPI application
      |
      +-- identity and approvals
      +-- brand intelligence and context packs
      +-- ideas, content, scripts, production
      +-- agent runtime and skills
      +-- memory, research, analytics, proof
      +-- integration adapters
      |
      +--> PostgreSQL
      +--> local object storage
      +--> dedicated BrandOS vault
      +--> optional OpenAI, Telegram, Apify, Creed Memory

FastAPI heartbeat worker
      |
      +--> same PostgreSQL, vault, and policy services
```

## Runtime policy

- PostgreSQL is the operational source of truth.
- Immutable version tables preserve canonical history.
- A dedicated vault is a human-readable approved-knowledge layer.
- External integrations implement typed adapters and default to disabled/mocked.
- High-risk actions call one backend approval service.
- Slow work is represented by idempotent database jobs before a separate queue is justified.
- Every meaningful agent run records intent, context, skills, tools, model alias, cost, confidence, writes, approvals, errors, and next actions.

## Frontend

- Next.js App Router and TypeScript
- Tailwind CSS design tokens
- TanStack Query for authenticated API state and Zod for capture validation
- client components for forms, boards, editors, offline replay, and feedback
- responsive shell with a desktop sidebar and mobile navigation drawer
- authenticated global search and a `Ctrl/Cmd+K` command palette
- manifest, service worker, install metadata, and an origin-local offline idea queue
- service-worker caches never cache API requests; offline ideas replay only after connectivity returns

## Backend

- FastAPI
- Pydantic settings and request/response models
- SQLAlchemy 2
- Alembic
- PostgreSQL with UUIDs and JSON fields; deterministic lexical retrieval is active
- embedding configuration is represented honestly as disabled or pending; pgvector is not installed
- pytest contract and integration tests
- a durable heartbeat worker with date-level idempotency and a disabled-by-default schedule

## Data and recovery boundary

- PostgreSQL owns operational records and approval state.
- Docker volumes own PostgreSQL data, uploaded originals, and the BrandOS vault.
- Backups combine a PostgreSQL custom-format dump with separate vault and object-storage archives.
- Every backup contains a migration identifier and SHA-256 checksums.
- Recovery tests restore into an isolated temporary database before a backup is trusted.

## Trust boundaries

1. Browsers never receive provider keys.
2. Telegram updates are untrusted until sender and webhook verification pass.
3. External research is untrusted evidence and cannot modify canonical strategy directly.
4. Model output is proposed data until schema, policy, and approval checks pass.
5. Creed Memory output is retrieved context with provenance, not BrandOS canonical truth.
6. Public actions remain unavailable in MVP without explicit approved records and an enabled adapter.
7. Offline capture stores only the founder-entered idea payload in browser-local storage; it never stores credentials or API responses.
8. The local single-user login is not an authorization to expose the application to the public internet.
