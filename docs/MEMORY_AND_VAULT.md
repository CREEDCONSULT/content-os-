# Memory and Vault

Last verified: 2026-07-23

## Authority model

- PostgreSQL is the operational source of truth.
- The dedicated Markdown vault is the human-readable knowledge layer.
- Semantic embedding is adapter-gated and currently disabled because no embedding
  model alias is configured.
- Creed Memory is a separate, disabled adapter. This repository does not modify
  `C:\CreedAI`.

The local Compose stack stores the vault in the persistent `brandos-vault` volume.
An explicit host path can be selected later with `BRANDOS_VAULT_PATH`; HA-001
records the required decision.

## Synchronization

`POST /api/v1/memory/vault/sync`:

1. initializes the supplied 14-area Obsidian folder structure;
2. exports canonical brand documents, approved scripts, and daily briefs;
3. stores a checksum, authority, provenance, and vault path in PostgreSQL;
4. imports founder-created Markdown notes;
5. creates Ideas from new notes under `03_Ideas/Inbox`;
6. preserves both sides and records a conflict when a canonical file changes;
7. refuses to export any configured secret value.

Writes use an atomic temporary-file replacement. Important notes are archived or
conflicted; they are not silently deleted.

## Retrieval

`GET /api/v1/memory/search?q=...` provides deterministic lexical retrieval ranked
by task terms, canonical authority, and confidence. Agent context packs now include
relevant non-restricted, non-conflicting vault records in addition to canonical
brand documents.

This is an honest MVP fallback for unavailable pgvector. It does not claim semantic
embedding quality.

## Knowledge graph

BrandOS now has a dedicated memory graph target described in
[BRANDOS_MEMORY_GRAPH_SPEC.md](BRANDOS_MEMORY_GRAPH_SPEC.md).

Implemented first slice:

- `knowledge_entities` stores normalized people, projects, platforms, pillars,
  audience segments, sources, campaigns, and other graph nodes.
- `knowledge_edges` stores typed relationships between entities, memory records,
  and operational BrandOS records.
- `POST /api/v1/memory/graph/extract` builds deterministic graph edges from
  existing structured records without requiring embeddings or AI extraction.
- API startup seeding also routes deterministic graph data so seeded deployments
  do not boot with empty graph tables.
- `GET /api/v1/memory/graph/neighborhood` returns nearby linked records for graph
  navigation.
- `GET /api/v1/memory/graph/search` searches graph entities and edges.

CreedAI remains external/read-only-by-default. BrandOS graph records must not be
merged into the existing CreedAI vault without an explicit migration plan.
