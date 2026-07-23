# Human Action Queue

Missing credentials do not block mock-backed local development. Never paste secrets into source files or Git.

## HA-001 — Confirm dedicated vault location

- Exact action: Approve the production BrandOS vault path.
- Why: The source recommends `C:\CreedAI\vaults\Mezie-BrandOS`, but the existing CreedAI system currently uses a different vault tree.
- Where: Set `BRANDOS_VAULT_PATH` in local `.env`.
- Required value: An absolute path owned by BrandOS.
- Security warning: Do not point BrandOS at the existing canonical CreedAI vault without an explicit migration plan.
- Blocked: Live bidirectional vault synchronization.
- Fallback: Repository-local ignored `vault/` directory or Docker volume.

## HA-002 — Configure OpenAI

- Exact action: Add a project-scoped API key and approved model aliases.
- Why: Live generation, transcription, vision, embeddings, and structured outputs require a provider.
- Where: Local `.env` or deployment secret manager.
- Required values: `OPENAI_API_KEY`, `BRAND_QUALITY_MODEL`, `BRAND_FAST_MODEL`, `BRAND_VISION_MODEL`, `BRAND_TRANSCRIPTION_MODEL`, `BRAND_EMBEDDING_MODEL`.
- Security warning: Never commit or place the key in browser-visible variables.
- Blocked: Live AI runs.
- Fallback: Deterministic mock provider with visible Mock status.

## HA-003 — Configure Telegram

- Exact action: Create or select a dedicated bot and provide the founder's numeric Telegram user ID.
- Why: Sender verification and message capture require bot credentials and an allowlist.
- Where: Local `.env` or deployment secret manager.
- Required values: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_ALLOWED_USER_IDS`.
- Security warning: Use a dedicated bot; never expose the token to the frontend or model prompts.
- Blocked: Live Telegram capture and approvals.
- Fallback: Signed webhook fixtures and local adapter tests.

## HA-004 — Configure Apify

- Exact action: Supply a scoped token and explicitly approve Actor IDs.
- Why: Some creator/platform acquisition paths require Apify.
- Where: Local `.env` or deployment secret manager.
- Required values: `APIFY_TOKEN`, `APIFY_APPROVED_ACTOR_IDS`, `APIFY_DAILY_BUDGET_USD`.
- Security warning: Unapproved or paid Actors must remain blocked.
- Blocked: Live paid creator acquisition.
- Fallback: Manual URLs/files, metadata-only evidence, and mock acquisition.

## HA-005 — Confirm Creed Memory access

- Exact action: Decide whether BrandOS may use the local CreedAI Memory API and provide its key through `.env`.
- Why: The adapter can retrieve founder/project context without touching canonical CreedAI notes.
- Where: `CREED_MEMORY_ENABLED`, `CREED_MEMORY_URL`, and `CREEDAI_MEMORY_API_KEY`.
- Required value: Existing local API key; do not create a second key in this repository.
- Security warning: The key remains server-side and must never be logged.
- Blocked: Live Creed Memory retrieval.
- Fallback: BrandOS-local source imports and mock adapter.

## HA-006 — Confirm missing canonical inputs

- Exact action: Supply the Founder Identity OS and any separate UI Component Design Specification if they exist.
- Why: Both are named by the build mandate but absent from the supplied files.
- Where: Add to the source-material folder for a controlled import.
- Required value: Original files, not reconstructed summaries.
- Security warning: Classify sensitive founder details before import.
- Blocked: Direct comparison against the upstream identity source.
- Fallback: Use the Positioning Architecture and Execution Handbook as available canonical derivatives.

## HA-007 — Choose remote deployment and domain

- Exact action: Select the deployment environment and domain after local release gates pass.
- Why: Secure cookies, CORS, webhooks, object storage, backups, and TLS depend on deployment topology.
- Where: Deployment configuration.
- Required values: Base domain and hosting/provider choice.
- Security warning: Do not expose the local-only auth build directly to the public internet.
- Blocked: Production deployment and Telegram webhook registration.
- Fallback: Local Docker Compose and private network access only.
