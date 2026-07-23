# Local Development

## Current prerequisite versions

- Git 2.54+
- Node.js 24+
- npm 11+
- Python 3.11 or 3.12
- uv 0.11+
- Docker Desktop with Compose

## Frontend only

```powershell
npm install
npm run dev
```

In a second terminal, initialize and run the API:

```powershell
Set-Location apps/api
uv sync
uv run alembic upgrade head
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```

The frontend is available at `http://localhost:3100`; the API and interactive
OpenAPI schema are available at `http://localhost:8000` and
`http://localhost:8000/docs`.

## Full stack

The canonical commands are:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Or use the rerunnable bootstrap helper:

```powershell
.\scripts\bootstrap.ps1
```

The committed values are local bootstrap values, not production credentials.
Replace `AUTH_PASSWORD`, `SESSION_SECRET`, and `POSTGRES_PASSWORD`, enable HTTPS,
and set `SECURE_COOKIES=true` before remote exposure.

## Validation

```powershell
npm run check
docker compose config --quiet
```

API-specific checks:

```powershell
Set-Location apps/api
uv run ruff check .
uv run pytest
uv run alembic check
```
