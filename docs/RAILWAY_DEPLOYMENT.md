# Railway deployment runbook

This is the safe path for a private Railway pilot of Mezie BrandOS. It is not the final public-release posture yet: keep it password-gated until the remaining public-release findings in `docs/DEPLOYMENT.md` are closed.

## Target Railway project

Create one Railway project with these services:

- `Postgres`: Railway PostgreSQL plugin/service.
- `api`: GitHub repo service from `CREEDCONSULT/content-os-`.
- `web`: second GitHub repo service from the same repo.
- `heartbeat`: hold for phase 2. Do not deploy it as a separate Railway service until vault/object storage is externalized, because Railway volumes are attached per service and the local Docker Compose heartbeat currently shares the API vault/storage volumes.

## API service

Use these Railway build/deploy settings:

- Source repo: `CREEDCONSULT/content-os-`
- Branch: `main`
- Root directory: leave blank / repo root
- Dockerfile path variable: `RAILWAY_DOCKERFILE_PATH=/apps/api/Dockerfile`
- Healthcheck path: `/health` from the root `railway.json`
- Public networking: generate a Railway HTTPS domain
- Volume: mount one Railway volume at `/app/data`

Set these API variables in Railway:

```dotenv
APP_ENV=production
AUTH_MODE=local
AUTH_USERNAME=mezie
AUTH_PASSWORD=<generate-new-strong-password>
SESSION_SECRET=<generate-new-64-byte-secret>
SECURE_COOKIES=true
SESSION_TTL_SECONDS=43200
LOGIN_RATE_LIMIT_ATTEMPTS=8
LOGIN_RATE_LIMIT_WINDOW_SECONDS=300

DATABASE_URL=postgresql+psycopg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
SOURCE_DOCUMENTS_PATH=/app/source-documents
OBJECT_STORAGE_PATH=/app/data/storage
BRANDOS_VAULT_PATH=/app/data/vault
MAX_UPLOAD_MB=250

APP_BASE_URL=https://${{web.RAILWAY_PUBLIC_DOMAIN}}
API_BASE_URL=https://${{api.RAILWAY_PUBLIC_DOMAIN}}
CORS_ORIGINS=https://${{web.RAILWAY_PUBLIC_DOMAIN}}

AI_PROVIDER=openai
OPENAI_API_KEY=<rotated-openai-api-key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=60
BRAND_FAST_MODEL=gpt-4.1-mini
BRAND_QUALITY_MODEL=gpt-4.1
BRAND_VISION_MODEL=gpt-4.1
BRAND_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
BRAND_EMBEDDING_MODEL=text-embedding-3-small
DAILY_MODEL_BUDGET_USD=1
WEEKLY_RESEARCH_BUDGET_USD=5

TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=<rotated-telegram-bot-token>
TELEGRAM_WEBHOOK_SECRET=<generate-new-telegram-webhook-secret>
TELEGRAM_ALLOWED_USER_IDS=7861471225
```

Notes:

- Rename `Postgres`, `api`, or `web` references if Railway names your services differently.
- Generate new OpenAI and Telegram credentials before entering them. The earlier pasted values should be treated as exposed.
- Keep the API public only because Telegram needs a webhook URL; authentication and Telegram secret-token validation still protect the sensitive routes.

## Web service

Use these Railway build/deploy settings:

- Source repo: `CREEDCONSULT/content-os-`
- Branch: `main`
- Root directory: leave blank / repo root
- Dockerfile path variable: `RAILWAY_DOCKERFILE_PATH=/apps/web/Dockerfile`
- Healthcheck path: `/health` from the root `railway.json`
- Public networking: generate a Railway HTTPS domain

Set these web variables in Railway:

```dotenv
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://${{api.RAILWAY_PUBLIC_DOMAIN}}
```

If the API public domain is generated after the first web build, redeploy the web service after setting `NEXT_PUBLIC_API_BASE_URL`; the Next.js client bundle needs that value at build time.

## Telegram webhook activation

After the API service is deployed and has a public Railway HTTPS domain, point Telegram at the API webhook:

```powershell
.\scripts\railway-set-telegram-webhook.ps1 -ApiBaseUrl "https://<api-domain>"
```

The script reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET` from the current environment or from `.env`, and does not print either secret.

## Smoke test checklist

Run this after both services deploy:

1. Open `https://<web-domain>/login`.
2. Sign in with the Railway `AUTH_USERNAME` and `AUTH_PASSWORD`.
3. Verify the dashboard loads live data.
4. Open `https://<api-domain>/health`; it should return healthy status.
5. Send an allowlisted Telegram message to the bot and confirm it appears in the dashboard.
6. Create one idea from the dashboard and confirm it persists after an API redeploy.

## Phase 2 before public launch

- Move vault/object storage to S3/R2 or another shared durable store.
- Re-enable the separate heartbeat worker once storage is shared.
- Replace single-password auth with a reviewed remote identity/access perimeter.
- Close the dependency/security findings tracked in `docs/DEPLOYMENT.md`.
