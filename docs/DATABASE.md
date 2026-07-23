# Database

PostgreSQL 16 is the operational source of truth. SQLAlchemy models use UUID
identifiers and UTC timestamps; Alembic owns schema evolution. The current head is
`4ca6a901f2f5`.

## Table ownership

| Area | Tables | Important invariants |
|---|---|---|
| Brand | `brands`, `brand_documents`, `brand_document_versions` | Canonical content is append-only; active versions change through approval |
| Ideation and lifecycle | `ideas`, `content_items`, `pipeline_events` | Full 15-state lifecycle; backend transitions enforce readiness and approval |
| Studio | `content_briefs`, `scripts`, `script_versions`, `hook_options`, `fact_checks` | Script versions are immutable; approval targets an exact version |
| Planning | `capacity_plans`, `calendar_events`, `production_plans`, `production_scenes`, `production_shots`, `production_checklist_items` | Capacity conflicts fail; readiness is server-computed |
| Evidence | `assets`, `proof_items` | Originals are checksummed and rights-classified; proof is permission-gated |
| Intelligence | `memory_records`, `sync_events`, `creators`, `benchmark_contents`, `insights`, `metric_snapshots`, `experiments` | Provenance, confidence, Demo state, and sync conflicts remain explicit |
| Operations | `telegram_messages`, `heartbeat_settings`, `heartbeat_runs`, `daily_briefs`, `tasks` | Telegram updates and heartbeat dates are idempotent |
| Agent governance | `skill_definitions`, `context_packs`, `agent_runs`, `approvals`, `audit_events` | Runs disclose context, budgets, tools, writes, errors, and approvals |

## Migration chain

1. `c06caa04f0c9` — initial operational schema.
2. `dd607cc884a2` — agent runtime and skill registry.
3. `db0eecfedeeb` — briefs, scripts, hooks, and fact checks.
4. `2378e805851a` — calendar, production, assets, and proof.
5. `4ca6a901f2f5` — memory, intelligence, Telegram, heartbeat, and analytics.

The PWA, offline queue, and global search use existing records and require no
schema change.

## Operational commands

```powershell
docker compose exec api .venv/bin/alembic current
docker compose exec api .venv/bin/alembic check
docker compose exec api .venv/bin/alembic upgrade head
```

Never edit a live table manually to bypass an approval or lifecycle rule. Create a
new migration for schema changes and use application services for state changes.

## Data outside PostgreSQL

- `/app/storage`: uploaded binary originals, addressed by database metadata and SHA-256.
- `/app/vault`: human-readable BrandOS memory with checksums and sync provenance.
- Browser local storage: pending offline idea payloads only, replayed into the API.

See [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) for the complete recovery unit.
