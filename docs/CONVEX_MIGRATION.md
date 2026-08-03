# Convex database migration

This project now has a Convex migration lane beside the existing FastAPI/Postgres backend. The safe cutover strategy is:

1. Mirror the SQL schema into Convex with `sqlId` fields that preserve original SQL primary keys.
2. Export SQL rows to JSONLines.
3. Import those JSONLines into Convex with table-level replace.
4. Verify Convex reads with indexed smoke queries.
5. Move app read/write paths table-by-table once the imported data is proven.

The live Railway deployment still uses Postgres until the read/write cutover is implemented. Railway web has `NEXT_PUBLIC_CONVEX_URL` set to the Convex production URL so client-side Convex queries can be introduced safely.

## Local dev deployment

Convex was initialized as a cloud dev deployment:

- Project: `dante-creed:mezie-brandos`
- Dev deployment: `abundant-alpaca-705`
- Production deployment: `tangible-finch-244`
- Production URL: `https://tangible-finch-244.convex.cloud`

Start/sync Convex functions:

```powershell
npx convex dev --once
```

## Regenerate schema from SQL models

```powershell
uv run --directory apps/api python ../../scripts/generate-convex-schema.py
```

The generated schema intentionally keeps most fields optional so existing imported rows do not deadlock future schema pushes.

## Export SQL data

From the local `.env` database:

```powershell
uv run --directory apps/api python ../../scripts/export-convex-jsonl.py
```

From the Railway Postgres service through a temporary local SSH tunnel without printing secrets:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseRailwaySshTunnel
```

If the Windows profile does not have an SSH key available to Railway, use a temporary Railway TCP proxy. The script deletes the proxy it creates after export/import:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseTemporaryRailwayTcpProxy
```

## Import SQL data into Convex

Dev deployment:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseRailwayApiDatabase
```

If the Railway private hostname is not resolvable locally, use:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseRailwaySshTunnel
```

If SSH tunneling is unavailable, use:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseTemporaryRailwayTcpProxy
```

Production deployment, after `npx convex deploy`:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseRailwayApiDatabase -Prod
```

Or, when exporting from the private Railway database:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseRailwaySshTunnel -Prod
```

If SSH tunneling is unavailable:

```powershell
.\scripts\migrate-sql-to-convex.ps1 -UseTemporaryRailwayTcpProxy -Prod
```

The script defaults to `replace` mode, so each mentioned Convex table is atomically replaced with the latest SQL export. Use `-Mode append` only for append-only test imports.

## Smoke queries

```powershell
npx convex run brandos:migrationOverview
npx convex run brandos:activeBrand
npx convex run brandos:recentIdeas '{\"limit\":5}'
```

## Cutover note

This first migration preserves SQL foreign keys as string fields such as `brandId`, `ideaId`, and `contentItemId`. That keeps the first import deterministic and auditable. A later Convex-native cutover can remap those to Convex `Id<...>` values table-by-table after imported data is verified.
