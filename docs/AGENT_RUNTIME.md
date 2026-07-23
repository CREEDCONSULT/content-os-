# Agent Runtime

Last verified: 2026-07-23

## Runtime contract

The Mezie Brand Director is a governed router over specialist skill contracts. A
run follows this sequence:

1. Persist the run before execution.
2. Validate the global input envelope.
3. Route the intent to one or more persisted skill definitions.
4. Build the smallest sufficient context pack from active canonical versions.
5. Check permissions, high-risk intent, and the daily model budget.
6. Create a backend approval and stop when the action is consequential.
7. Call the configured model provider for safe internal work.
8. Persist the structured output, sources, proposed writes, completed writes,
   approvals, cost fields, confidence, errors, and next actions.
9. Add a durable audit event.

The API never treats a proposed write as a completed write. The current runtime
does not execute model-proposed database mutations.

## Skill registry

Thirty skill definitions are imported from
`docs/source/skills/Mezie_BrandOS_Skill_Library_v1`. Each persisted record includes:

- version and source checksum;
- triggers and required context;
- allowed tools and workflow;
- input and output schema requirements;
- memory, approval, and failure policies;
- model profile, timeout, cost class, and enabled state.

Routing is deterministic and inspectable. Unknown intents fall back to
`29_general_brand_assistant`. Every route also includes the Skill Router, Context
Pack Builder, and Agent Transparency skills.

## Context packs

Context packs rank active canonical records by task relevance and authority. Each
source reference includes the document ID, immutable version ID, source path,
classification, authority, and checksum. The pack records a token estimate,
freshness notes, and explicit exclusions.

The current retrieval implementation is deterministic keyword and authority
ranking. Semantic retrieval and embeddings are Milestone 7 work.

## Providers

`AI_PROVIDER=mock` is the safe default. The mock provider:

- makes no network call;
- spends no money;
- writes nothing;
- labels its result as deterministic development output.

`AI_PROVIDER=openai` selects the server-only OpenAI Responses API adapter. It
requires both `OPENAI_API_KEY` and `BRAND_FAST_MODEL`. Missing values fail the run
honestly and do not fall back silently. The adapter requests a strict JSON Schema
response and uses `store: false`.

The adapter shape follows the official OpenAI
[Responses API migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses)
and
[Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs).
It has not been live-tested because no project credential or approved model alias
is configured.

## Approval and budget enforcement

The runtime creates a pending backend approval before:

- public publishing or scheduling;
- external outreach;
- destructive deletion;
- canonical or brand-boundary changes;
- audience redefinition;
- sensitive founder-story use;
- investment signals;
- projected daily model spend above `DAILY_MODEL_BUDGET_USD`.

An approval decision does not automatically resume or execute a blocked agent run.
Resumption is intentionally deferred until a reviewed job runner exists.

## API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/agent/skills` | List typed skill definitions |
| `GET` | `/api/v1/agent/runs` | List transparent runs |
| `POST` | `/api/v1/agent/runs` | Route and execute a governed request |
| `GET` | `/api/v1/agent/runs/{id}` | Inspect one run |
| `GET` | `/api/v1/agent/context-packs/{id}` | Inspect context and provenance |

## Current limitations

- The OpenAI path is implemented but not live-verified.
- Token usage is recorded when returned, but USD price calculation is not yet
  configured; live cost remains `0` until a reviewed pricing table exists.
- Context retrieval is not yet semantic.
- Approved blocked runs do not auto-resume.
- No public, paid, or destructive tool is available to the runtime.
