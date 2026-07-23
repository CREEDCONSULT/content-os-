# Assets and Proof of Work

Last verified: 2026-07-23

## Asset ingestion

The authenticated upload endpoint:

- enforces a configurable 250 MB maximum before persistence;
- strips directory components and normalizes unsafe filenames;
- stores the original bytes behind the API using an atomic temporary-file rename;
- computes SHA-256 and links duplicates to the first matching record;
- records MIME type, size, tags, relationships, and rights state;
- never returns an absolute server filesystem path.

Rights default to `unknown`. Operators can explicitly select `owned`, `licensed`,
or `restricted` and attach supporting notes. BrandOS does not infer ownership.

The seeded asset is metadata-only, visibly marked `DEMO`, and has
`original_preserved: false`; no fabricated media file is implied.

## Proof records

Each proof item separates:

- credibility gap;
- context and constraints;
- process and output;
- result and lessons;
- evidence links and linked asset IDs;
- sensitivity and permission status.

A new proof record becomes `verified` only when at least one evidence reference
exists and its permission gate passes. Client-confidential proof requires
`permission_status: approved`; otherwise it remains `evidence_needed`.

The current workflow records evidence state. It does not publish case studies or
send client material externally.

## API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/assets` | List safe asset metadata |
| `POST` | `/api/v1/assets` | Upload, checksum, preserve, and classify an original |
| `GET` | `/api/v1/proof` | List proof records |
| `POST` | `/api/v1/proof` | Create a permission-aware proof record |
