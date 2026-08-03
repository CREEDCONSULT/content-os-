# BrandOS Memory Graph Specification

Status: accepted target architecture  
Owner: BrandOS platform  
Created: 2026-08-03  
Related docs:

- [MEMORY_AND_VAULT.md](MEMORY_AND_VAULT.md)
- [DECISION_LOG.md](DECISION_LOG.md)
- [HUMAN_ACTION_QUEUE.md](HUMAN_ACTION_QUEUE.md)
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

## 1. Executive decision

BrandOS should own a dedicated memory system, wiki file system, and knowledge
graph.

BrandOS should not merge directly into the existing CreedAI memory vault or use
CreedAI as its canonical source of truth. CreedAI may be used as an external
context adapter and optional downstream summary destination, but the BrandOS
memory graph must remain BrandOS-owned.

This is a true and valuable course of action because BrandOS memory has a
different purpose than CreedAI memory:

- CreedAI memory is operational and agent-centered.
- BrandOS memory is brand, content, strategy, proof, audience, and decision
  centered.
- BrandOS requires stronger provenance, approval, canonical-version control,
  content lineage, rights boundaries, and graph retrieval.
- Mixing the systems would make it harder to know which memory is canonical,
  which memory is private, which memory is safe to publish, and which memory
  belongs to the BrandOS product itself.

The correct relationship is:

```text
BrandOS database = operational source of truth
BrandOS vault    = human-readable wiki layer
BrandOS graph    = relationship and retrieval layer
CreedAI memory   = optional read-only context adapter at first
```

## 2. Current implementation baseline

The current repository already contains the foundation for this architecture.

### Already implemented or documented

- PostgreSQL is the operational source of truth.
- A dedicated BrandOS Markdown vault is the human-readable knowledge layer.
- Memory records exist in the backend through `memory_records`.
- Vault sync is implemented through `/api/v1/memory/vault/sync`.
- Vault initialization creates the BrandOS folder system.
- Memory search exists as deterministic lexical retrieval.
- Context packs include relevant memory records for agent runs.
- Sync events are recorded through `sync_events`.
- Canonical status, confidence, sensitivity, provenance, checksums, review dates,
  sync status, embedding status, and demo flags are already represented.
- Creed Memory is environment-gated and separate.
- Existing decisions say CreedAI integration should happen by contract, not
  source copy.

### Not yet fully implemented

- Explicit graph entities.
- Explicit graph edges or backlinks table.
- Entity extraction from memory notes, content, proof, scripts, creators, and
  analytics.
- Hybrid retrieval using lexical search, embeddings, and graph traversal.
- User-facing graph UI.
- Obsidian-style backlinks generated from the database graph.
- Approval workflow for promoting graph facts into canonical memory.
- Live CreedAI read-only adapter.
- Approved BrandOS summary export back to CreedAI.

## 3. Product purpose

The BrandOS memory graph exists to make the product increasingly intelligent
about one brand over time.

It should answer questions like:

- What do we already know about the founder?
- Which audience segments does this content idea serve?
- Which proof records support this claim?
- Which ideas became scripts, shoots, published posts, and measurable outcomes?
- Which hooks, stories, formats, and platforms are working?
- Which decisions are canonical, stale, contradicted, or restricted?
- Which content pieces are connected to which campaigns, pillars, benchmarks,
  and proof assets?
- What context should an agent receive before writing, reviewing, planning, or
  publishing?

The graph should turn BrandOS from a content dashboard into a compounding
brand-intelligence operating system.

## 4. Authority model

BrandOS memory has three coordinated layers.

| Layer | Role | Canonical authority |
|---|---|---|
| Database | Operational source of truth, permissions, sync ledger, indexes, graph edges | Yes |
| Vault/wiki | Human-readable Markdown memory, Obsidian-style browsing, manual notes | No, unless synced and approved |
| Graph/retrieval | Relationships, context assembly, semantic navigation, lineage | Derived authority from database records |

The vault is not allowed to silently override canonical database truth.

If a vault file changes underneath an existing canonical record, the system must
preserve both sides and create a conflict event. Canonical records are promoted
through approval, not by file overwrite.

## 5. Dedicated vault/wiki file system

The BrandOS vault should remain separate from the existing CreedAI vault.

Recommended production path:

```text
C:\CreedAI\vaults\Mezie-BrandOS
```

Acceptable alternatives:

- A different absolute path explicitly owned by BrandOS.
- A Docker volume for hosted environments.
- A repo-local ignored `vault/` directory for local fallback only.

Do not point BrandOS at the existing canonical CreedAI vault without a separate
migration plan.

### Vault top-level areas

The current vault structure should remain the base wiki taxonomy:

```text
00_Command_Center
01_Brand_Core
02_Content_Strategy
03_Ideas
04_Benchmarks
05_Research
06_Content_Development
07_Production
08_Published_Content
09_Analytics
10_Proof_of_Work
11_Founder_Stories
12_Agent_Memory
13_Templates
99_Archive
```

### Graph-generated wiki additions

The graph layer should add generated index files without replacing the existing
folder structure:

```text
00_Command_Center/Memory Graph Index.md
00_Command_Center/Open Conflicts.md
00_Command_Center/Pending Approvals.md
01_Brand_Core/Entity Index.md
01_Brand_Core/Canonical Decisions/Decision Map.md
02_Content_Strategy/Pillar Map.md
03_Ideas/Idea Lineage.md
08_Published_Content/Content Lineage.md
09_Analytics/Lessons Graph.md
10_Proof_of_Work/Claim Evidence Map.md
12_Agent_Memory/Context Pack Log.md
12_Agent_Memory/Graph Maintenance.md
```

These files are generated views. Human edits should be imported as notes or
review comments, not treated as automatic canonical graph mutations.

## 6. Core graph concepts

### 6.1 Memory record

A memory record is a durable piece of BrandOS knowledge.

Current fields already exist:

- `brand_id`
- `memory_type`
- `title`
- `content`
- `canonical_status`
- `confidence`
- `provenance`
- `vault_path`
- `content_checksum`
- `sensitivity`
- `review_at`
- `sync_status`
- `embedding_status`
- `is_demo`

Memory records are the first graph node type and should remain the canonical
bridge between database state and Markdown vault state.

### 6.2 Knowledge entity

A knowledge entity is a normalized thing the system can recognize, link, and
reuse across records.

Proposed entity types:

| Entity type | Examples |
|---|---|
| `person` | Founder, collaborator, creator, client, public figure |
| `brand` | Mezie, Creed Consult, client brand, competitor |
| `project` | BrandOS, CreedAI, campaign, service line |
| `platform` | LinkedIn, Instagram, X, YouTube, TikTok, newsletter |
| `audience_segment` | founders, consultants, traders, operators |
| `content_pillar` | Build, Leverage, Own, Lead, See, Create |
| `campaign` | monthly theme, launch sequence, proof sprint |
| `idea` | captured idea, selected idea, archived idea |
| `content_item` | brief, script, carousel, video, post, newsletter |
| `asset` | image, video, transcript, proof screenshot, document |
| `claim` | positioning claim, credibility claim, performance claim |
| `proof` | case study, testimonial, evidence record, metric |
| `decision` | accepted architecture/product/brand decision |
| `source` | source document, benchmark, URL, research note |
| `skill` | BrandOS skill definition or agent capability |
| `experiment` | content experiment, hook test, platform test |
| `metric` | view count, save rate, CTR, conversion, qualitative signal |

Suggested table or Convex collection:

```text
knowledge_entities
- id
- brand_id
- entity_type
- name
- slug
- description
- aliases
- canonical_status
- sensitivity
- confidence
- provenance
- first_seen_at
- last_seen_at
- review_at
- is_demo
- created_at
- updated_at
```

Unique rule:

```text
brand_id + entity_type + slug
```

Aliases should be additive. Do not merge two entities automatically if the merge
would affect canonical records, restricted records, or proof claims.

### 6.3 Knowledge edge

A knowledge edge is a typed relationship between two graph nodes.

Edges may connect:

- memory record to memory record;
- memory record to entity;
- entity to entity;
- app record to memory record;
- app record to entity;
- vault path to database record;
- content item to proof, platform, campaign, audience, creator, or metric.

Suggested table or Convex collection:

```text
knowledge_edges
- id
- brand_id
- source_type
- source_id
- target_type
- target_id
- relationship_type
- label
- evidence
- confidence
- canonical_status
- sensitivity
- provenance
- created_by
- approved_by
- approved_at
- valid_from
- valid_until
- review_at
- is_demo
- created_at
- updated_at
```

Unique rule:

```text
brand_id + source_type + source_id + relationship_type + target_type + target_id
```

Edges should be append-only when canonical. If a relationship changes, create a
superseding edge and archive the old edge.

### 6.4 Context pack

A context pack is a task-specific bundle of memory used by an agent.

The current `context_packs` model should remain, but it should eventually include
graph traversal metadata:

```text
context_packs.source_records       existing
context_packs.context_markdown     existing
context_packs.token_estimate       existing
context_packs.freshness_notes      existing
context_packs.exclusions           existing
context_packs.graph_traversal      proposed
context_packs.retrieval_strategy   proposed
context_packs.feedback_score       proposed
```

The system should remember which context packs led to useful outputs so future
retrieval can improve without treating model-generated text as canonical truth.

## 7. Relationship taxonomy

Use a controlled set of relationship types. Free-form relationship labels may be
stored for display, but retrieval and analytics should rely on stable
relationship types.

### Core authority edges

| Relationship | Meaning |
|---|---|
| `derived_from` | Node was created from another source |
| `supersedes` | Node replaces an older node |
| `contradicts` | Node conflicts with another node |
| `supports` | Node provides support for another node |
| `requires_approval_for` | Node cannot be used without approval |
| `restricted_by` | Node is limited by sensitivity, rights, or policy |
| `canonicalizes` | Node promotes a working record into canonical memory |

### Brand and strategy edges

| Relationship | Meaning |
|---|---|
| `expresses` | Content expresses a brand pillar, value, or positioning point |
| `targets` | Content or campaign targets an audience segment |
| `belongs_to` | Node belongs to a campaign, pillar, project, or platform |
| `uses_voice_pattern` | Content uses a known language or tone pattern |
| `uses_story_pattern` | Content uses a founder/storytelling pattern |
| `maps_to_offer` | Content or proof supports an offer |

### Content lifecycle edges

| Relationship | Meaning |
|---|---|
| `became_brief` | Idea was converted into a brief |
| `became_script` | Brief or idea became a script |
| `became_shoot_plan` | Script became production plan |
| `published_as` | Content item became a published post |
| `uses_asset` | Content uses an image, video, transcript, or document |
| `inspired_by` | Content references a benchmark or source |
| `adapts` | Content adapts a benchmark into original Mezie form |

### Proof and analytics edges

| Relationship | Meaning |
|---|---|
| `proves` | Proof record substantiates a claim |
| `needs_evidence_for` | Claim or content requires proof before use |
| `performed_with` | Published content produced a metric |
| `validated` | Experiment or metric validated a hypothesis |
| `invalidated` | Experiment or metric invalidated a hypothesis |
| `suggests` | Weak signal suggests a possible future direction |

### Integration edges

| Relationship | Meaning |
|---|---|
| `imported_from` | BrandOS imported context from an external system |
| `syncs_summary_to` | Approved BrandOS summary may sync outward |
| `references_external` | Node links to external URL/tool/system |
| `captured_from` | Node came from Telegram, upload, web clip, or manual entry |

## 8. Memory types

Memory records should use stable memory types. Suggested values:

```text
brand_truth
canonical_decision
founder_story
audience_insight
content_pillar
campaign_memory
idea_note
script_memory
production_memory
published_content_memory
creator_intelligence
benchmark_pattern
research_note
proof_record
analytics_lesson
experiment_lesson
agent_preference
agent_run_summary
rejected_idea
vault_note
working_note
```

The system may support additional types, but each type must map to:

- an allowed vault folder;
- allowed sensitivities;
- default review window;
- default graph extraction behavior;
- allowed publication/retrieval use.

## 9. Sensitivity and approval model

Sensitivity levels:

```text
public
internal
sensitive
restricted
```

Canonical statuses:

```text
working
canonical
archived
restricted
```

Recommended lifecycle:

```text
captured -> working -> candidate -> approved -> canonical -> superseded -> archived
```

Because the current backend only has `working`, `canonical`, `archived`, and
`restricted`, the first implementation can represent `candidate` and `approved`
through approval records or provenance metadata. A later migration can add
explicit statuses if needed.

Approval rules:

- Public use of internal or sensitive memory requires policy checks.
- Canonical brand truth requires approval.
- Founder stories require sensitivity classification before retrieval.
- Proof claims require evidence before being used as public credibility claims.
- Restricted records never enter ordinary context packs.
- CreedAI imports never become canonical automatically.
- AI-generated graph edges are suggestions until approved or deterministically
  derived from trusted records.

## 10. Retrieval model

The retrieval system should move in stages.

### Stage 1: deterministic lexical retrieval

Current state:

- Search memory by query terms.
- Exclude restricted records.
- Exclude conflict records.
- Rank by term match, confidence, and canonical authority.
- Build context packs with selected source records and provenance.

This is sufficient for MVP behavior.

### Stage 2: hybrid search

Add:

- Embedding records for memory content.
- Embedding records for entity descriptions.
- Embedding records for content items, scripts, proof, and benchmark summaries.
- Hybrid rank = lexical score + semantic score + authority score + freshness
  score + graph distance score.

Required configuration:

```text
BRAND_EMBEDDING_MODEL
```

The system must visibly disclose when embeddings are disabled and fall back to
lexical search.

### Stage 3: graph traversal retrieval

For agent context packs, retrieve:

1. directly relevant canonical documents;
2. directly relevant memory records;
3. entities mentioned by the task;
4. one-hop edges from those entities;
5. high-confidence supporting proof;
6. stale/conflicting exclusions;
7. restricted/sensitive exclusions;
8. prior context packs with useful outcomes.

Context packs should include:

- why each item was included;
- authority level;
- source path or record id;
- checksum or version id;
- freshness note;
- exclusion note when something important was withheld.

## 11. CreedAI boundary

BrandOS should use CreedAI memory in three phases.

### Phase A: no live coupling

Default state:

- Creed Memory disabled.
- BrandOS vault and database operate independently.
- Mock adapter may show integration readiness.

### Phase B: read-only context adapter

If approved through environment configuration:

```text
CREED_MEMORY_ENABLED=true
CREED_MEMORY_URL=http://localhost:8788
CREEDAI_MEMORY_API_KEY=<server-side only>
```

Then BrandOS may retrieve founder/project context from CreedAI.

Rules:

- Never write directly into the CreedAI canonical vault.
- Never expose the API key to the frontend.
- Never log the API key.
- Label CreedAI-derived memory as external.
- Store provenance on any imported summary.
- Treat imported context as working memory until reviewed.

### Phase C: approved summary export

Only approved summaries may sync outward.

Allowed exports:

- high-level BrandOS preferences;
- approved brand summaries;
- non-sensitive project status summaries;
- agent-useful lessons explicitly approved for general CreedAI use.

Disallowed exports:

- raw founder stories;
- restricted memories;
- private credentials;
- unapproved proof claims;
- unpublished strategy;
- direct canonical source files;
- conflict records.

## 12. API surface

Current routes:

```text
GET  /api/v1/memory/records
POST /api/v1/memory/records
GET  /api/v1/memory/search
POST /api/v1/memory/vault/initialize
POST /api/v1/memory/vault/sync
GET  /api/v1/memory/sync-events
```

Proposed graph routes:

```text
GET  /api/v1/memory/entities
POST /api/v1/memory/entities
GET  /api/v1/memory/entities/{entity_id}
PATCH /api/v1/memory/entities/{entity_id}

GET  /api/v1/memory/edges
POST /api/v1/memory/edges
PATCH /api/v1/memory/edges/{edge_id}

POST /api/v1/memory/graph/extract
GET  /api/v1/memory/graph/neighborhood
GET  /api/v1/memory/graph/search
GET  /api/v1/memory/graph/conflicts
GET  /api/v1/memory/graph/pending-approvals
POST /api/v1/memory/graph/export-wiki-indexes
```

Optional Convex mapping:

```text
memoryRecords
knowledgeEntities
knowledgeEdges
syncEvents
contextPacks
graphExtractionJobs
```

The product concepts should stay stable whether the backend remains PostgreSQL,
migrates to Convex, or runs a hybrid transition.

## 13. UI surface

Add a dedicated Memory area to the web app.

Recommended navigation:

```text
/memory
/memory/search
/memory/records/:id
/memory/entities/:id
/memory/graph
/memory/conflicts
/memory/approvals
/memory/context-packs
/memory/vault-sync
```

Core UI features:

- searchable memory records;
- entity index;
- graph neighborhood view;
- backlinks on each record;
- source/provenance panel;
- sensitivity badge;
- canonical status badge;
- conflict queue;
- approval queue;
- sync history;
- context-pack preview;
- “why was this included?” explanation for agent context.

The first UI does not need a complex force-directed graph. A practical graph
neighborhood list is more valuable:

```text
This record
├─ supports: claim
├─ belongs_to: content pillar
├─ targets: audience segment
├─ derived_from: source document
├─ became_script: script
└─ proved_by: proof record
```

## 14. Agent behavior

Agents must treat memory as governed state, not casual prompt stuffing.

Before writing or analyzing, an agent should:

1. identify task intent;
2. request a context pack;
3. retrieve canonical brand truth;
4. retrieve relevant graph neighborhood;
5. disclose exclusions and freshness limits;
6. perform the task;
7. propose memory writes separately from the answer;
8. request approval before canonical or sensitive memory writes.

Agents may write working notes automatically only when:

- the user explicitly asks to remember something;
- the note is internal or public;
- no sensitive details or credentials are present;
- the note does not alter canonical brand truth;
- provenance is captured.

## 15. Data ingestion

Ingestion sources:

- manual web app entry;
- Markdown vault notes;
- Telegram captures;
- source documents;
- script/brief/pipeline events;
- production plans;
- published content records;
- analytics imports;
- proof records;
- creator/benchmark intelligence;
- CreedAI read-only context adapter;
- approved external research adapters.

Every ingestion event must produce:

- source type;
- source reference;
- timestamp;
- actor or system;
- sensitivity classification;
- checksum when file/text based;
- confidence;
- review requirement;
- sync status.

## 16. Graph extraction

Graph extraction should start deterministic and become AI-assisted only where
useful.

### Deterministic extraction

Use structured database fields to create edges:

- idea -> brief;
- brief -> script;
- script -> production plan;
- production plan -> asset;
- content item -> platform;
- published content -> metric;
- proof -> claim;
- creator -> benchmark content;
- memory record -> vault path;
- brand document -> active version.

### AI-assisted extraction

Use an AI provider to suggest:

- entities mentioned in long notes;
- claims inside scripts;
- implied audience segments;
- proof requirements;
- story patterns;
- reusable lessons;
- contradictions;
- candidate backlinks.

AI-assisted extraction must mark output as suggested unless the relation is
approved or validated by deterministic evidence.

## 17. Conflict handling

Conflict sources:

- vault file changes after database export;
- duplicate canonical decisions;
- contradictory claims;
- entity merge ambiguity;
- sensitive memory requested by ordinary context pack;
- CreedAI import contradicts BrandOS canonical memory;
- proof claim lacks evidence.

Conflict response:

1. preserve both sides;
2. create a sync event or graph conflict record;
3. exclude conflict nodes from ordinary context packs;
4. show conflict in UI;
5. require approval or explicit resolution;
6. archive superseded records instead of deleting silently.

## 18. Security and privacy

The memory graph must never store or export configured secrets.

Existing secret-scan behavior should remain mandatory for vault writes.

Additional rules:

- API keys remain server-side only.
- External adapters are environment-gated.
- Restricted memories are excluded by default.
- Sensitive founder stories require classification.
- Public-ready claims require proof status checks.
- Graph exports must respect sensitivity.
- Debug logs must never include raw secrets, restricted founder memory, or
  private content drafts.

## 19. Observability

Every graph mutation should be auditable.

Log:

- actor;
- operation;
- source node;
- target node;
- relationship type;
- provenance;
- sensitivity;
- approval status;
- before/after status;
- checksum where applicable.

Useful dashboards:

- graph health;
- unlinked records;
- stale records;
- restricted records excluded from recent packs;
- conflicts by type;
- pending approvals;
- most-used context sources;
- context packs that led to useful outputs;
- memory growth by type.

## 20. Implementation phases

### Phase 1: spec and model alignment

Deliverables:

- this specification;
- data migration plan;
- memory/entity/edge schema;
- API contract;
- UI wireframe;
- test plan.

### Phase 2: graph schema

Deliverables:

- `knowledge_entities`;
- `knowledge_edges`;
- validators/contracts;
- migrations;
- seed sample graph;
- unit tests.

### Phase 3: deterministic graph builder

Deliverables:

- create deterministic edges from existing records;
- link ideas, content, scripts, assets, proof, metrics, and vault records;
- expose graph neighborhood API;
- add sync/audit events.

### Phase 4: memory UI

Deliverables:

- `/memory`;
- record detail;
- entity detail;
- graph neighborhood;
- conflict queue;
- approval queue;
- context-pack preview.

### Phase 5: hybrid retrieval

Deliverables:

- embedding model configuration;
- embedding status transitions;
- hybrid ranking;
- graph-aware context packs;
- retrieval evaluation fixtures.

### Phase 6: CreedAI adapter

Deliverables:

- read-only CreedAI context retrieval;
- provenance labeling;
- restricted import handling;
- approved summary export;
- no direct mutation of CreedAI canonical vault.

### Phase 7: graph-generated wiki indexes

Deliverables:

- generated Markdown index files;
- backlink sections;
- claim-evidence maps;
- decision maps;
- content lineage pages;
- conflict and approval reports.

## 21. Acceptance criteria

The memory graph is acceptable when:

- BrandOS can initialize and sync its own dedicated vault.
- Memory records remain database-governed and provenance-rich.
- A user can see why a memory exists, where it came from, and whether it is
  canonical.
- A user can browse entity pages and backlinks.
- A user can inspect idea-to-published-content lineage.
- A user can inspect claim-to-proof lineage.
- Context packs use graph relationships and disclose exclusions.
- Restricted records are not retrieved by ordinary agent runs.
- CreedAI imports are labeled external and never canonical by default.
- Approved summaries can sync outward without leaking raw sensitive memory.
- Conflicts preserve both sides and require resolution.
- The graph works even when embeddings are disabled.

## 22. Immediate next engineering tasks

1. Add `knowledge_entities` and `knowledge_edges` models.
2. Add migration and test fixtures.
3. Add graph schemas to API contracts.
4. Add deterministic edge builder from existing database records.
5. Add `/api/v1/memory/graph/neighborhood`.
6. Add `/memory` UI page with record, entity, and edge views.
7. Add graph-aware context-pack retrieval.
8. Add generated wiki index export.
9. Add CreedAI read-only import adapter after human approval.
10. Add approved summary export only after sensitivity tests pass.

## 23. Non-goals

For the first implementation, do not:

- merge BrandOS into the existing CreedAI vault;
- copy the dirty CreedAI source tree into this repository;
- treat AI-generated relations as canonical;
- require embeddings for basic operation;
- build a fancy graph visualization before practical graph navigation works;
- sync sensitive founder stories outward;
- publish or expose memory records publicly;
- use the vault as the only operational source of truth.

## 24. Final architecture statement

BrandOS memory should be a governed product brain:

- database-backed;
- wiki-readable;
- graph-linked;
- provenance-heavy;
- approval-aware;
- agent-usable;
- CreedAI-compatible without being CreedAI-dependent.

That is the right long-term architecture for turning BrandOS into a compounding
brand operating system rather than a static content planner.
