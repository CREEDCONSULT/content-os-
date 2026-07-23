# Reusable CreedAI Components

Audit date: 2026-07-23
Source checkout: `C:\CreedAI` on `main` at observed commit `b5fc9c5a1d42b6cf3b582cafaf36a7e96f1e4efb`

The source checkout had substantial user-owned modified and untracked work. BrandOS therefore reuses stable contracts and patterns, not an unreviewed source copy.

| Component | Observed boundary | BrandOS reuse decision |
|---|---|---|
| CreedAI Memory API | Local health passed on `127.0.0.1:8788`; documented endpoints are `/query`, `/brief`, `/profile`, `/route-task` | Implement an environment-gated, read-only HTTP adapter with timeouts, server-only key handling, source-path provenance, and honest unavailable state |
| Memory scopes | `founder`, `personal`, `creedConsult`, `Volatile`, `Ghost`, `CreedAI`, `content` | Preserve explicit scope selection and cross-domain isolation; never rely on similarity alone |
| Obsidian/Qdrant retrieval rules | Vault is canonical for CreedAI; vectors are rebuildable | Do not write into the CreedAI vault; BrandOS keeps its own operational DB and dedicated vault while treating Creed results as retrieved context |
| Creator Intelligence/CCIS schemas | Source record, research report, Actor evaluation, evidence statuses | Adapt evidence-level fields and provenance into BrandOS source/benchmark models |
| CCIS acquisition policy | Source normalization, cache, trust registry, budget checks, approved Actor gating, manual fallback | Reimplement behind a BrandOS adapter; no live paid Actor runs without explicit configuration and approval |
| Creator analysis rule | No URL-only analysis; no scene/visual claims without collected visual evidence | Enforce in schemas, UI labels, tests, and agent output validators |
| Model adapter pattern | Small provider protocol, deterministic mock, configurable route | Use a typed async provider interface with a deterministic mock and OpenAI Responses adapter |
| Telegram capture pattern | Sender allowlist, capture-only surface, attachment preservation, private paths not exposed | Reuse the boundary; BrandOS writes dashboard records and never treats Telegram as canonical memory |
| Provenance and run metadata | Source paths, provider/model identity, limitations, review state | Carry through Context Packs, Agent Runs, research records, and UI transparency panels |

## Explicit non-reuse

- No modification of `C:\CreedAI`.
- No dependency on the existing PowerShell process supervisor for BrandOS startup.
- No use of the existing general vault as the detailed BrandOS content vault.
- No assumption that untracked CCIS code is a stable package.
- No copying of secrets, `.env`, raw personal notes, or private source material.
