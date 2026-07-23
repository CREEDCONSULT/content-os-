# Creator Intelligence

Last verified: 2026-07-23

Creator Intelligence supports a tiered watchlist and manual benchmark URLs. It
stores operator-supplied evidence, hook and structure observations, visual/editing
notes, transferable mechanics, protected-identity boundaries, original Mezie
adaptation prompts, pattern tags, and limitations.

The current adapter never downloads third-party media or calls Apify. When Apify is
disabled, each teardown says so. URL-only captures remain queued until evidence is
added.

## Copying safeguard

- Creator-specific identity, exact wording, signature phrases, and distinctive
  visual branding are classified as protected.
- The service checks generated adaptations against supplied source text using an
  eight-word overlap boundary.
- Adaptations ask for original Mr. C. Mezie language and first-party evidence.
- Metadata-only evidence cannot be presented as verified performance.

## API

| Method | Route |
|---|---|
| `GET`, `POST` | `/api/v1/intelligence/creators` |
| `GET`, `POST` | `/api/v1/intelligence/benchmarks` |
