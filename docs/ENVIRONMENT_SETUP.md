# Environment Setup

1. Copy `.env.example` to `.env`.
2. Keep external integrations disabled until credentials and budgets are intentionally configured.
3. Generate strong values for `AUTH_PASSWORD` and `SESSION_SECRET` before remote access.
4. Confirm `BRANDOS_VAULT_PATH` before enabling bidirectional vault synchronization.
5. Do not copy `C:\CreedAI\.env` into this repository.

## Integration states

Each integration must report one of:

- `disabled`
- `mock`
- `configured`
- `healthy`
- `degraded`
- `error`

`configured` does not mean `healthy`; health requires a successful live contract check.

## Secrets

The application may read secret values only in backend processes. Integration-status endpoints return booleans or redacted metadata, never secret values.
