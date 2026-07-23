# Architecture

## Confirmed topology

Mezie BrandOS is a modular monolith with explicit module boundaries.

```text
Next.js web/PWA
      |
      | REST + later SSE
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
      +--> PostgreSQL / pgvector
      +--> local object storage
      +--> dedicated BrandOS vault
      +--> optional OpenAI, Telegram, Apify, Creed Memory
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
- server components for initial reads where practical
- client components for forms, boards, editors, and optimistic feedback
- responsive shell with desktop sidebar and mobile bottom navigation
- future TanStack Query, Zustand, React Hook Form, Zod, TipTap, DnD Kit, and Recharts introduced only with the slices that use them

## Backend

- FastAPI
- Pydantic settings and request/response models
- SQLAlchemy 2
- Alembic
- PostgreSQL with UUIDs, JSONB, full text, and pgvector-ready boundaries
- pytest contract and integration tests

## Trust boundaries

1. Browsers never receive provider keys.
2. Telegram updates are untrusted until sender and webhook verification pass.
3. External research is untrusted evidence and cannot modify canonical strategy directly.
4. Model output is proposed data until schema, policy, and approval checks pass.
5. Creed Memory output is retrieved context with provenance, not BrandOS canonical truth.
6. Public actions remain unavailable in MVP without explicit approved records and an enabled adapter.
