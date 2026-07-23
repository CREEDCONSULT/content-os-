# API

FastAPI serves the local API at `http://localhost:8000`. `/health` and `/ready`
are public health probes. All `/api/v1` workspace routes require the signed
`brandos_session` HttpOnly cookie except the login endpoint and the separately
verified Telegram webhook.

Interactive OpenAPI is available at `/docs` on a trusted local workstation.

## Route groups

| Prefix | Capability |
|---|---|
| `/api/v1/auth` | Login, current user, logout |
| `/api/v1/dashboard` | Command-center summary |
| `/api/v1/brand` | Canonical document reads, immutable versions, approval submission |
| `/api/v1/ideas` | Capture, filter, edit, score |
| `/api/v1/content` | Lifecycle list/detail and governed transitions |
| `/api/v1/studio` | Briefs, scripts, immutable versions, fact checks, submission |
| `/api/v1/calendar` | Weekly capacity and conflict-checked events |
| `/api/v1/production` | Plans, scenes, shots, logistics, critical checklists |
| `/api/v1/assets` | Rights-aware multipart upload and deduplicated listing |
| `/api/v1/proof` | Evidence and permission-aware proof ledger |
| `/api/v1/agent` | Skill catalog, transparent runs, context packs |
| `/api/v1/approvals` | Pending decisions and auditable approval/rejection |
| `/api/v1/memory` | Memory records, lexical retrieval, vault initialization/sync/events |
| `/api/v1/intelligence` | Creator watchlist and benchmark teardown |
| `/api/v1/telegram` | Signed webhook, fixture capture, message ledger |
| `/api/v1/heartbeat` | Manual runs, schedule settings, daily briefs |
| `/api/v1/analytics` | Metrics, partial-row CSV import, insights, experiments |
| `/api/v1/integrations` | Redacted adapter status |
| `/api/v1/search` | Authenticated cross-module search for the command palette |

## Error semantics

- `400`: invalid state or policy violation.
- `401`: authentication missing or invalid.
- `403`: permission, sender, rights, or approval boundary.
- `404`: record not found.
- `409`: capacity conflict, idempotency conflict, or unsafe transition.
- `413`: upload/import exceeds its limit.
- `422`: request contract failed validation.
- `429`: bounded login attempts exceeded; response includes `Retry-After`.

API responses include `X-Request-ID`, clickjacking and MIME protections, a
referrer policy, and `Cache-Control: no-store` for `/api` responses.

## Contract rules

- Never treat a `Demo`, mock, partial, disabled, or pending record as live.
- A successful model response is still only a proposal until policy and approval pass.
- Publishing is unavailable; no route silently performs a public action.
- Global search excludes restricted memory and requires at least two characters.
- Offline replay calls the ordinary idea endpoint, so it cannot bypass validation.
- Provider credentials are server-only and integration status is redacted.
