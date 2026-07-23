# Decision Log

## ADR-001 - Modular monolith

- Date: 2026-07-23
- Status: accepted
- Decision: Use a Next.js web application, FastAPI modular backend, PostgreSQL, a database-backed job model, local object storage, and explicit external adapters in one repository.
- Reason: This matches the implementation-specific architecture and keeps the single-founder MVP debuggable.
- Reversal condition: A measured scaling or isolation need justifies extracting a module.

## ADR-002 - Python compatibility boundary

- Date: 2026-07-23
- Status: accepted
- Decision: Application code supports Python 3.11 and 3.12; Docker uses Python 3.12.
- Reason: The workstation has Python 3.11.9 while the specification prefers 3.12+. Blocking on a host upgrade would not improve the MVP.
- Reversal condition: Host Python is upgraded and a dependency requires 3.12-only features.

## ADR-003 - PostgreSQL operational truth; vault human-readable knowledge

- Date: 2026-07-23
- Status: accepted
- Decision: BrandOS operational state lives in PostgreSQL. Approved knowledge is exported to a dedicated BrandOS vault. CreedAI remains an external, read-only-by-default memory integration.
- Reason: The BrandOS technical specification is more specific than the existing CreedAI vault-first convention.
- Reversal condition: A proven offline-first requirement demands a different replication model.

## ADR-004 - Full lifecycle with compact UI grouping

- Date: 2026-07-23
- Status: accepted
- Decision: Preserve all 15 PRD pipeline states in the backend. The default board groups them into Ideation, Scripting, Production, Review, and Published, with an expanded view available.
- Reason: This satisfies the safety and audit requirements without sacrificing the approved mockup's clarity.
- Reversal condition: Usability tests show another default grouping is clearer.

## ADR-005 - Execution Handbook content allocation

- Date: 2026-07-23
- Status: accepted
- Decision: Seed planning targets use Build 30%, Leverage 20%, Own 15%, Lead 15%, See 10%, Create 10%.
- Reason: The Execution Handbook is the operationally specific source and balances the Create pillar better than the earlier 35/20/15/15/10/5 mix.
- Reversal condition: Founder explicitly approves a different allocation.

## ADR-006 - External integrations default off

- Date: 2026-07-23
- Status: accepted
- Decision: OpenAI, Telegram, Apify, and Creed Memory adapters are environment-gated. Deterministic mocks are the default.
- Reason: Missing credentials must not block development, and mock status must remain explicit.
- Reversal condition: A configured integration passes its live contract tests.

## ADR-007 - CreedAI integration by contract, not source copy

- Date: 2026-07-23
- Status: accepted
- Decision: Reuse stable API/schema concepts and implement BrandOS-owned adapters. Do not copy the dirty `C:\CreedAI` checkout wholesale.
- Reason: The existing checkout contains user changes and untracked components. Contract integration preserves isolation and provenance.
- Reversal condition: A clean tagged CreedAI package is made available for direct dependency use.

## ADR-008 - Canonical changes are append-only and approval-gated

- Date: 2026-07-23
- Status: accepted
- Decision: Editing a canonical brand document creates a new immutable version and a pending approval. The active canonical pointer changes only after backend approval.
- Reason: The PRD explicitly prohibits overwriting canonical records.
- Reversal condition: None within MVP.

## ADR-009 - Isolated local web port

- Date: 2026-07-23
- Status: accepted
- Decision: Bind Mezie BrandOS to host port `3100` while keeping the container on port `3000`.
- Reason: The current workstation already runs Creed/Open WebUI on port `3000`. BrandOS must not stop, reuse, or mutate that existing service. `BRANDOS_WEB_PORT` remains configurable for other environments.
- Reversal condition: The host port becomes available and the founder explicitly chooses to move the application.
