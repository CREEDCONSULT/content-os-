# Deployment

## Verified local deployment

```powershell
Copy-Item .env.example .env
# Rotate AUTH_PASSWORD and SESSION_SECRET in .env.
.\scripts\bootstrap.ps1
```

Open `http://localhost:3100`. The API is at `http://localhost:8000`. BrandOS uses
port 3100 specifically to avoid the existing service on port 3000.

Docker Compose runs:

- PostgreSQL 16 with a persistent volume and readiness probe.
- FastAPI with migration/seed startup, storage/vault volumes, and health probe.
- A separate durable heartbeat worker.
- A standalone Next.js production server with a health probe.

## Configuration gates

For any production-like environment:

- set `APP_ENV=production`;
- set unique `AUTH_PASSWORD` and high-entropy `SESSION_SECRET`;
- set `SECURE_COOKIES=true`;
- set exact HTTPS `CORS_ORIGINS`, `APP_BASE_URL`, `API_BASE_URL`, and
  build-time `NEXT_PUBLIC_API_BASE_URL`;
- terminate TLS before web and API;
- keep PostgreSQL and API off the public network;
- provide an encrypted external backup destination;
- run the security, test, migration, and recovery gates.

Provider credentials must be project-scoped server secrets. Enable OpenAI,
Telegram, Apify, or Creed Memory only after its contract is live-tested.

## Public-release no-go

Do not expose this build publicly while `R-012` and `R-015` remain active. A
public release needs a supported dependency remediation and a reviewed remote
identity/access perimeter, plus real-device PWA/accessibility/performance evidence.

## Rollback

Application rollback uses a previously built Git commit/image only when its
migration compatibility is known. Data rollback uses a verified backup and
`scripts/restore.ps1`; never use `git reset` or volume deletion as a data recovery
method.
