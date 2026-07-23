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
| API tests | `npm run test:api` | 8 passed; 2 dependency deprecation warnings |
| Production web build | `npm run build` | Passed; 11 static App Router routes generated |
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
