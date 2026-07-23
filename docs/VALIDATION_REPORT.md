# Validation Report

Date: 2026-07-23

Scope: repository bootstrap and the first connected Brand Intelligence, Ideas, and
Content Lifecycle slice.

## Automated validation

| Check | Command | Result |
|---|---|---|
| Web lint | `npm run lint:web` | Passed |
| API lint | `npm run lint:api` | Passed |
| Web type check | `npm run typecheck` | Passed |
| Web tests | `npm run test:web` | 7 passed |
| API tests | `npm run test:api` | 24 passed; 2 dependency deprecation warnings |
| Production web build | `npm run build` | Passed; 20 static App Router routes generated |
| Complete code gate | `npm run check` | Passed |
| Compose validation | `docker compose config --quiet` | Passed |
| PostgreSQL migration drift | `docker compose exec -T api .venv/bin/alembic check` | Passed; no new upgrade operations |
| Container health | `docker compose ps` | PostgreSQL, API, and web healthy |

## Live API smoke

Authenticated smoke checks ran against `http://localhost:8000` using the documented
local bootstrap account.

| Probe | Result |
|---|---|
| `GET /health` | `ok: true` |
| `GET /ready` | `ok: true`, database ready |
| `GET /api/v1/dashboard/summary` | Live aggregate returned |
| `GET /api/v1/brand/documents` | 52 records |
| `GET /api/v1/ideas` | 6 records |
| `GET /api/v1/content` | 7 records |
| Dashboard idea metric | 6, matching persisted idea count |

One idea named `Browser QA: live capture verified` was created through the real UI
during the smoke test. It is not marked as demo data and intentionally remains in
the local persistent volume as evidence that browser capture reached PostgreSQL.

## Browser validation

The authenticated application was exercised in Chrome against the live Compose
stack.

- Login completed with an HttpOnly session.
- Command Center rendered live API totals and visible demo disclosures.
- Idea capture persisted and updated the dashboard total from 5 to 6.
- Brand Intelligence rendered all 52 imported documents.
- A brand document detail exposed its original source path and
  `system:source-import` provenance.
- The five operational pipeline lanes rendered seven content records while the API
  retained all 15 lifecycle states.
- Settings disclosed OpenAI as a deterministic mock and unconfigured adapters as
  disabled.
- The dashboard and navigation were exercised at `390 x 844`; the mobile drawer
  opened correctly.
- Chrome warning/error log query returned no entries.

## Dependency security

`npm audit` reports:

- 0 critical;
- 3 high;
- 0 moderate;
- 0 low.

The findings are in Next.js transitive `postcss` and `sharp` dependencies. Registry
verification reports Next.js `16.2.11` as the latest stable version. npm's suggested
forced remediation would install Next.js `9.3.3`, a breaking and unsafe downgrade,
so it was not applied. R-012 remains a public-release blocker.

## Release verdict for this slice

The connected local slice is usable and reproducible. It is approved for continued
local MVP development. It is not approved for public deployment because dependency
R-012 and remote-authentication hardening R-015 remain open.

## Agent runtime increment

The Milestone 4 runtime added four API tests, bringing the API total to 12 and the
repository total to 19.

| Check | Result |
|---|---|
| Skill import | 30 typed definitions persisted from supplied contracts |
| Mock execution | Completed with 5 routed skills, 4 canonical sources, and 0 writes |
| Context provenance | Active document and version IDs, paths, authority, and checksums returned |
| Idempotency | Repeated key returned the original run |
| Budget enforcement | Above-ceiling request created a pending backend approval |
| Publishing enforcement | Public-publish intent created a pending backend approval |
| Migration cycle | `upgrade -> downgrade -1 -> upgrade -> check` passed on SQLite |
| Live PostgreSQL migration | `c06caa04f0c9 -> dd607cc884a2` passed |
| Agent Console | ESLint, TypeScript, and Next.js production build passed |

The live OpenAI path was not called. No credential or model alias is configured,
and deterministic mock mode remains visibly active.

## Brief and script increment

Milestone 5 adds three API tests and a complete non-demo live smoke.

| Check | Result |
|---|---|
| Idea to brief | Linked brief and content item created without overwriting source idea |
| Script versioning | Immutable versions, checksum, active pointer, and history passed |
| Hook Lab | Independent hook records and explainable scores returned |
| Fact check | Unresolved and unsourced claims block approval |
| Financial safety | Guaranteed returns and direct buy signals blocked |
| Revision reset | New version reset fact-check and approval state |
| Script approval | Exact version created pending approval and backend decision |
| Production gate | Non-demo content was blocked before approval and advanced after approval |
| Migration cycle | `upgrade -> downgrade -1 -> upgrade -> check` passed |
| Script Studio | ESLint, TypeScript, and Next.js production build passed |

The live local path used the persisted `Browser QA: live capture verified` idea. It
ended with a non-demo approved script and linked content in `ready_to_shoot`. No
public publishing or external provider call occurred.

## Calendar, production, assets, and proof increment

Milestone 6 adds four API tests and four operator workspaces.

| Check | Result |
|---|---|
| Weekly capacity | Hour, shoot-count, and edit-count conflicts return `409` |
| Production approval gate | Draft or unapproved scripts cannot create plans |
| Production readiness | Plan remains blocked until logistics and every critical pre-shoot item pass |
| Lifecycle boundary | Generic transition cannot bypass a missing 100% production plan |
| Asset preservation | Original bytes, SHA-256, safe storage key, rights state, and duplicate link verified |
| Proof evidence | Missing evidence and missing confidential-client permission remain `evidence_needed` |
| Migration cycle | `upgrade -> downgrade db0eecfedeeb -> upgrade -> check` passed |
| Live PostgreSQL | Migration `2378e805851a` is current with no schema drift |
| Live seeded records | 3 events, 3 capacity plans, 1 blocked plan, 1 asset, and 1 proof item returned |
| Web routes | `/calendar`, `/production`, `/assets`, and `/proof` each returned HTTP `200` |

The live smoke was read-only after seeding. The one production plan remains
intentionally blocked with four disclosed blockers; the smoke did not manufacture a
ready state or fabricate proof.

## Memory, intelligence, Telegram, heartbeat, and analytics increment

Milestones 7–11 add five API tests and three operator workspaces.

| Check | Result |
|---|---|
| Vault initialization | Complete dedicated folder tree created under isolated persistent storage |
| Database → vault | Canonical documents, approved scripts, and daily briefs exported atomically |
| Vault → database | Founder Markdown imported; Inbox note created one linked Idea |
| Conflict handling | Manual canonical edit preserved; sync event recorded conflict |
| Context retrieval | Relevant non-restricted, non-conflicting memory joins canonical sources |
| Creator safeguard | Protected identity separated; eight-word copying boundary passed |
| Telegram security | Missing secret `401`; non-allowlisted sender `403`; duplicate update idempotent |
| Telegram voice E2E | Signed/local transcript fixture created an Idea and retained Demo disclosure |
| Heartbeat deduplication | Different keys on the same date returned one durable run and brief |
| Heartbeat scheduler | Compose worker healthy; database settings and daily idempotency enforced |
| CSV import | Two valid rows persisted while one invalid row was rejected with an exact error |
| Insight safety | Import observation explicitly avoided causal claims |
| Experiment | One variable and three control conditions persisted |
| Migration cycle | `upgrade -> downgrade 2378e805851a -> upgrade -> check` passed |

Live PostgreSQL smoke:

- migration `4ca6a901f2f5` at head;
- 54 Markdown records exported with zero conflicts;
- manual heartbeat returned `partial`, two opportunities, and `$0.00` cost;
- Telegram voice fixture created an Idea and remained marked Demo;
- three creators, one benchmark, one metric, one insight, and one experiment loaded;
- `/benchmarks`, `/intelligence`, and `/analytics` returned HTTP `200`.

No external scraping, live Telegram message, paid call, public schedule, or publish
action occurred.
