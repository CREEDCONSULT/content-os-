# MEZIE BRAND OS
# TECHNICAL ARCHITECTURE SPECIFICATION

**Version:** 1.0  
**Status:** Implementation architecture  
**Date:** July 2026  
**System:** Mezie Brand OS  
**Architecture Style:** Modular monolith with asynchronous workers  
**Primary Deployment:** Local-first, web-accessible, PWA-enabled  
**Primary User:** Single founder  
**Future Compatibility:** Multi-user and multi-brand

---

# 1. ARCHITECTURE OBJECTIVE

The system shall provide a stable technical foundation for:

- Brand strategy management
- Content operations
- AI agent orchestration
- Skill execution
- Creator and trend research
- Persistent memory
- Obsidian vault synchronization
- Telegram interaction
- File and media management
- Analytics
- Approval workflows
- Scheduled heartbeat jobs
- Future platform integrations

The architecture should be simple enough for an MVP but structured so that high-value modules can later be separated into services.

---

# 2. ARCHITECTURAL PRINCIPLES

1. Modular monolith before microservices.
2. Postgres as operational source of truth.
3. Obsidian vault as human-readable knowledge source.
4. Explicit synchronization between database and vault.
5. Asynchronous jobs for slow or expensive work.
6. Skills as versioned application modules.
7. Human approval before public or high-risk actions.
8. Provider abstraction for AI models and external tools.
9. Full provenance and run logging.
10. Local-first development with production-ready boundaries.
11. Server-side secrets only.
12. Idempotent background jobs.
13. API-first internal design.
14. Typed schemas across frontend, backend, and agent runtime.
15. Observability from the beginning.

---

# 3. RECOMMENDED STACK

## 3.1 Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zustand
- React Hook Form
- Zod
- TipTap
- DnD Kit
- Recharts
- Lucide icons
- Framer Motion
- PWA manifest and service worker

The Next.js App Router supports file-system routing and current React server/client patterns, while the official PWA guidance covers manifests, service workers, installation, and push notifications. citeturn179587search0turn179587search1

## 3.2 Backend

- FastAPI
- Python 3.12+
- Pydantic
- SQLAlchemy 2
- Alembic
- httpx
- OpenAI Python SDK
- APScheduler for early local scheduling
- Redis and Dramatiq, RQ, or Celery for production workers
- WebSockets or Server-Sent Events for job updates

FastAPI supports in-process background tasks for small operations, but its own documentation recommends a larger queue system for heavy computation or multi-process execution. citeturn179587search3

## 3.3 Database

- PostgreSQL
- pgvector
- JSONB
- Full-text search
- Row-level access controls at application layer for MVP

## 3.4 Object Storage

Development:

- Local filesystem

Production:

- S3-compatible storage

Options:

- Cloudflare R2
- AWS S3
- MinIO
- Backblaze B2

## 3.5 Cache and Queue

MVP:

- Database-backed jobs
- Local cache

Production:

- Redis
- Worker process
- Distributed locks
- Rate limiting

## 3.6 AI

- OpenAI Responses API
- Configurable model aliases
- OpenAI transcription
- OpenAI vision-capable model
- Optional realtime voice later
- Provider interface for additional models later

The official OpenAI quickstart documents server-side SDK use and built-in capabilities such as web search, file search, function calling, and remote MCP. citeturn179587search15

## 3.7 External Tools

- Telegram Bot API
- Apify
- FFmpeg
- YouTube transcript or API workflows
- Web search
- Creed Memory
- Obsidian vault
- Google Drive later
- Social platform APIs later

Telegram’s Bot API is an HTTP interface designed for server-side bot integrations and supports message and media interactions. citeturn179587search2turn179587search11

---

# 4. HIGH-LEVEL ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                         │
│  Next.js Desktop | Mobile PWA | Telegram | Future Voice    │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / WebSocket
┌──────────────────────────────▼──────────────────────────────┐
│                    APPLICATION GATEWAY                       │
│  Auth | Rate Limit | Request Validation | API Versioning    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    FASTAPI MODULAR CORE                      │
│                                                             │
│ Brand │ Ideas │ Content │ Scripts │ Production │ Analytics  │
│ Agent │ Skills│ Memory  │ Approvals│ Assets    │ Telegram   │
└──────────────┬──────────────────┬─────────────────┬─────────┘
               │                  │                 │
       ┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼────────┐
       │ PostgreSQL     │  │ Job Queue    │  │ Object Storage │
       │ + pgvector     │  │ + Scheduler  │  │ Media / Files  │
       └───────┬───────┘  └──────┬──────┘  └──────┬────────┘
               │                  │                 │
       ┌───────▼──────────────────▼─────────────────▼────────┐
       │             AGENT AND INTEGRATION LAYER              │
       │ OpenAI | Apify | Telegram | Web | FFmpeg | MCP       │
       └───────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────▼──────────────────────────────┐
       │          OBSIDIAN VAULT + CREED MEMORY SYNC          │
       └──────────────────────────────────────────────────────┘
```

---

# 5. DEPLOYMENT TOPOLOGY

## 5.1 Local Development

```text
Windows Host
├── Next.js dev server
├── FastAPI server
├── PostgreSQL
├── Redis optional
├── Worker
├── Scheduler
├── Local object storage
├── Obsidian vault
└── WSL tools / FFmpeg / Hermes integrations
```

## 5.2 Local Production Preview

Recommended:

- Docker Compose
- Reverse proxy
- HTTPS through local secure tunnel if needed
- Persistent volumes
- Daily backups

## 5.3 Cloud Production

```text
CDN / Edge
   ↓
Next.js Web
   ↓
FastAPI API
   ↓
PostgreSQL + Redis + Worker
   ↓
S3-compatible Object Storage
   ↓
Managed monitoring and backups
```

## 5.4 Recommended Domain Structure

```text
app.meziebrandos.com
api.meziebrandos.com
assets.meziebrandos.com
```

A single domain with `/api` may be used during MVP.

---

# 6. REPOSITORY STRUCTURE

```text
mezie-brandos/
├── apps/
│   ├── web/
│   │   ├── src/app/
│   │   ├── src/components/
│   │   ├── src/features/
│   │   ├── src/lib/
│   │   ├── public/
│   │   └── tests/
│   │
│   ├── api/
│   │   ├── app/main.py
│   │   ├── app/core/
│   │   ├── app/modules/
│   │   ├── app/agent/
│   │   ├── app/skills/
│   │   ├── app/integrations/
│   │   ├── app/workers/
│   │   ├── app/schemas/
│   │   ├── migrations/
│   │   └── tests/
│   │
│   └── telegram/
│       ├── handlers/
│       ├── commands/
│       └── tests/
│
├── packages/
│   ├── contracts/
│   ├── design-system/
│   ├── skill-schemas/
│   └── shared-config/
│
├── skills/
│   ├── 00_skill_router/
│   ├── 01_brand_strategy/
│   ├── ...
│   └── 29_general_brand_assistant/
│
├── vault-templates/
├── scripts/
├── infra/
│   ├── docker/
│   ├── compose/
│   └── deployment/
├── docs/
└── .env.example
```

---

# 7. BACKEND MODULES

## 7.1 Identity and Access

Responsibilities:

- User authentication
- Telegram identity mapping
- Session management
- Permissions
- API tokens
- Future role-based access

## 7.2 Brand Module

Responsibilities:

- Brand records
- Canonical documents
- Context packs
- Personas
- Pillars
- Series
- Boundaries
- Decisions
- Versioning

## 7.3 Ideas Module

Responsibilities:

- Capture
- Transcription linkage
- Scoring
- Deduplication
- Status
- Conversion to brief

## 7.4 Research Module

Responsibilities:

- Sources
- Topics
- Trend signals
- Daily briefs
- Creator watchlist
- Content teardowns
- Provenance

## 7.5 Content Module

Responsibilities:

- Campaigns
- Content items
- Briefs
- Calendar
- Pipeline
- Platform variants
- Publications

## 7.6 Script Module

Responsibilities:

- Scripts
- Versions
- Hooks
- Comments
- Approval
- Fact-check status
- Brand alignment

## 7.7 Production Module

Responsibilities:

- Production plans
- Scenes
- Shots
- Checklists
- Readiness
- Scheduling
- Review notes

## 7.8 Asset Module

Responsibilities:

- Upload
- Storage
- Metadata
- Preview
- Rights
- Tags
- Links
- Duplicate detection

## 7.9 Analytics Module

Responsibilities:

- Metric imports
- Normalization
- Insights
- Experiments
- Learnings
- Platform baselines

## 7.10 Proof Module

Responsibilities:

- Proof items
- Case studies
- Authority gaps
- Testimonials
- Public/private versions

## 7.11 Agent Module

Responsibilities:

- Agent sessions
- Skill routing
- Context loading
- Model invocation
- Tool execution
- Run logs
- Costs
- Confidence
- Approvals

## 7.12 Memory Module

Responsibilities:

- Vault sync
- Embeddings
- Retrieval
- Memory promotion
- Decision memory
- Creed Memory sync

## 7.13 Notification Module

Responsibilities:

- Telegram summaries
- In-app notifications
- Approval alerts
- Job completion
- Heartbeat report
- Future push notifications

---

# 8. DATA MODEL

## 8.1 Core Tables

```text
users
brands
brand_documents
brand_document_versions
context_packs
personas
content_pillars
content_series
brand_decisions
ideas
sources
creators
creator_watch_entries
benchmark_contents
research_records
trend_signals
daily_briefs
campaigns
content_items
content_briefs
scripts
script_versions
hooks
production_plans
scenes
shots
checklists
checklist_items
assets
asset_links
tasks
calendar_events
publications
metric_snapshots
insights
experiments
proof_items
case_studies
agent_runs
agent_run_steps
approvals
conversations
messages
telegram_messages
memory_records
memory_links
sync_events
integration_accounts
job_runs
notifications
audit_events
```

---

# 9. KEY ENTITY DEFINITIONS

## 9.1 BrandDocument

Fields:

- id
- brand_id
- document_type
- title
- slug
- canonical_status
- current_version_id
- vault_path
- sensitivity
- created_at
- updated_at

## 9.2 BrandDocumentVersion

Fields:

- id
- brand_document_id
- version_number
- content_markdown
- change_summary
- created_by
- approval_id
- created_at

## 9.3 Idea

Fields:

- id
- brand_id
- title
- raw_input
- source_type
- source_reference
- transcript_id
- pillar_id
- series_id
- audience_id
- status
- brand_fit_score
- audience_value_score
- proof_score
- timeliness_score
- originality_score
- feasibility_score
- total_priority_score
- rejection_reason
- created_at
- updated_at

## 9.4 ContentItem

Fields:

- id
- brand_id
- campaign_id
- idea_id
- title
- platform
- format
- pillar_id
- series_id
- audience_id
- objective
- status
- priority
- publish_at
- published_at
- publication_url
- readiness_score
- owner_id
- created_at
- updated_at

## 9.5 Script

Fields:

- id
- content_item_id
- current_version_id
- approval_status
- fact_check_status
- brand_alignment_score
- created_at
- updated_at

## 9.6 ScriptVersion

Fields:

- id
- script_id
- version_number
- content_json
- plain_text
- duration_seconds
- model_alias
- prompt_version
- revision_reason
- created_by
- created_at

## 9.7 AgentRun

Fields:

- id
- request_id
- user_id
- brand_id
- channel
- intent
- status
- model_alias
- started_at
- completed_at
- input_tokens
- output_tokens
- model_cost
- tool_cost
- total_cost
- confidence
- context_pack_id
- summary
- error_code

## 9.8 Approval

Fields:

- id
- brand_id
- action_type
- target_type
- target_id
- requested_by
- requested_at
- risk_level
- cost_estimate
- status
- approved_by
- decided_at
- notes

## 9.9 MemoryRecord

Fields:

- id
- brand_id
- memory_type
- title
- content
- canonical_status
- confidence
- provenance
- vault_path
- embedding
- sensitivity
- review_at
- created_at
- updated_at

---

# 10. DATABASE DESIGN RULES

1. UUID primary keys.
2. UTC timestamps.
3. Soft delete for operational records.
4. Immutable version tables for canonical content.
5. JSONB for flexible script and skill outputs.
6. Foreign keys for core relationships.
7. Unique constraints for idempotent imports.
8. Partial indexes for active records.
9. GIN indexes for JSONB and full-text fields.
10. pgvector index for semantic retrieval.
11. Audit event for high-risk mutations.
12. Database migrations through Alembic.

---

# 11. API DESIGN

## 11.1 Style

- REST for primary CRUD
- WebSocket or SSE for job progress
- Webhooks for Telegram and future platforms
- Versioned routes under `/api/v1`

## 11.2 Example Routes

### Brand

```text
GET    /api/v1/brands/{brand_id}
GET    /api/v1/brands/{brand_id}/documents
POST   /api/v1/brands/{brand_id}/documents
POST   /api/v1/documents/{id}/versions
POST   /api/v1/documents/{id}/approve
POST   /api/v1/context-packs
```

### Ideas

```text
GET    /api/v1/ideas
POST   /api/v1/ideas
GET    /api/v1/ideas/{id}
PATCH  /api/v1/ideas/{id}
POST   /api/v1/ideas/{id}/score
POST   /api/v1/ideas/{id}/convert-to-brief
```

### Content

```text
GET    /api/v1/content
POST   /api/v1/content
PATCH  /api/v1/content/{id}
POST   /api/v1/content/{id}/transition
GET    /api/v1/calendar
POST   /api/v1/calendar/events
```

### Scripts

```text
POST   /api/v1/scripts
GET    /api/v1/scripts/{id}
POST   /api/v1/scripts/{id}/versions
POST   /api/v1/scripts/{id}/generate
POST   /api/v1/scripts/{id}/review
POST   /api/v1/scripts/{id}/approve
```

### Agent

```text
POST   /api/v1/agent/runs
GET    /api/v1/agent/runs/{id}
GET    /api/v1/agent/runs/{id}/events
POST   /api/v1/agent/runs/{id}/approve
POST   /api/v1/agent/chat
```

### Heartbeat

```text
POST   /api/v1/heartbeat/run
GET    /api/v1/heartbeat/runs
GET    /api/v1/heartbeat/runs/{id}
PATCH  /api/v1/heartbeat/settings
```

### Telegram

```text
POST   /api/v1/integrations/telegram/webhook
POST   /api/v1/integrations/telegram/test
```

### Analytics

```text
POST   /api/v1/analytics/import
GET    /api/v1/analytics/overview
GET    /api/v1/analytics/content/{id}
POST   /api/v1/experiments
```

---

# 12. EVENT MODEL

The system should emit internal events.

Examples:

```text
idea.created
idea.scored
brief.created
script.generated
script.approved
content.status_changed
production.ready
asset.uploaded
publication.recorded
metrics.imported
insight.created
experiment.completed
heartbeat.started
heartbeat.completed
approval.requested
approval.decided
memory.updated
```

Consumers:

- Notification service
- Vault sync
- Analytics
- Agent log
- Task creation
- Search indexing

MVP events may be implemented through a database outbox table.

---

# 13. JOB ARCHITECTURE

## 13.1 Job Types

- Transcription
- Embedding
- Creator acquisition
- Video metadata extraction
- FFmpeg frame extraction
- Script generation
- Fact checking
- Daily heartbeat
- Analytics import
- Vault sync
- Creed Memory sync
- Asset preview generation
- Notification delivery

## 13.2 Job Lifecycle

```text
queued
running
waiting_approval
succeeded
partial
failed
cancelled
retrying
```

## 13.3 Job Requirements

- Idempotency key
- Retry policy
- Timeout
- Cost budget
- Cancellation
- Progress
- Error details
- Parent run
- Result references

## 13.4 Scheduling

Development:

- Manual heartbeat
- APScheduler or OS scheduler

Production:

- Dedicated scheduler
- Queue worker
- Distributed lock

---

# 14. AGENT RUNTIME

## 14.1 Core Flow

```text
Request
→ Intent Classification
→ Skill Selection
→ Context Pack
→ Permission Check
→ Plan
→ Model or Tool Calls
→ Output Validation
→ Proposed Writes
→ Approval
→ Commit
→ Run Summary
```

## 14.2 Skill Registry

Each skill record includes:

- slug
- version
- title
- trigger patterns
- input schema
- output schema
- required context
- allowed tools
- approval policy
- memory policy
- timeout
- model profile
- enabled status

## 14.3 Model Aliases

```text
brand_quality_model
brand_fast_model
brand_vision_model
brand_transcription_model
brand_realtime_model
brand_embedding_model
```

Never hardcode a public model name throughout the application.

## 14.4 Tool Registry

Tools shall be registered with:

- name
- description
- input schema
- output schema
- cost class
- risk class
- timeout
- retry policy
- approval requirement

## 14.5 Structured Output

All agent outputs shall use typed schemas.

Example:

```json
{
  "skill": "08_scriptwriting",
  "status": "success",
  "summary": "Draft created",
  "outputs": {
    "script_id": "uuid",
    "hook_variants": [],
    "duration_estimate": 58
  },
  "sources": [],
  "memory_writes": [],
  "dashboard_writes": [],
  "approvals_required": [],
  "warnings": [],
  "next_actions": [],
  "confidence": 0.91
}
```

---

# 15. OPENAI INTEGRATION

## 15.1 Interface

Use the Responses API through a provider adapter.

## 15.2 Server-Side Only

API keys shall remain in backend environment variables or a secret manager.

## 15.3 Capabilities

- Text generation
- Structured outputs
- Image understanding
- File input
- Web search
- Function calling
- Remote MCP
- Streaming

## 15.4 Storage Policy

Do not rely on provider conversation state as the primary memory system. OpenAI documents endpoint-specific data controls and retention, so BrandOS should preserve required state in its own database and vault. citeturn179587search32

## 15.5 Batch

Use batch processing later for:

- Large benchmark archives
- Embeddings
- Historical script evaluation
- Analytics reprocessing

The OpenAI API supports asynchronous batch jobs. citeturn179587search34

---

# 16. MEMORY AND VAULT ARCHITECTURE

## 16.1 Source of Truth

Operational truth:

- PostgreSQL

Human-readable knowledge:

- Obsidian vault

Semantic retrieval:

- pgvector or existing Qdrant

General founder memory:

- Creed Memory

## 16.2 Vault Path

```text
C:\CreedAI\vaults\Mezie-BrandOS\
```

## 16.3 Vault Folders

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

## 16.4 Synchronization Rules

### Database to Vault

Write:

- Canonical documents
- Daily briefs
- Approved scripts
- Case studies
- Monthly reviews
- Major decisions

### Vault to Database

Import:

- Approved manual edits
- New notes in monitored folders
- Founder-created Markdown

### Conflict Resolution

- Version both copies
- Mark conflict
- Require user resolution for canonical records

## 16.5 Memory Promotion

```text
Raw Observation
→ Working Hypothesis
→ Repeated Pattern
→ Tested Insight
→ Approved Brand Learning
→ Canonical Principle
```

## 16.6 Retrieval Ranking

Rank by:

1. Canonical authority
2. Task relevance
3. Freshness
4. Confidence
5. Source quality
6. Sensitivity permission
7. Recency of use

---

# 17. CONTEXT PACK BUILDER

## Inputs

- Task intent
- Skill
- Platform
- Audience
- Content item
- Token budget
- Freshness requirement

## Retrieval Sources

- Brand documents
- Related memory
- Founder stories
- Recent analytics
- Benchmarks
- Current campaign
- Platform playbook

## Output

- Selected records
- Summaries
- Provenance
- Token estimate
- Missing context
- Excluded records

## Rule

Return the smallest sufficient context pack.

---

# 18. CREATOR INTELLIGENCE ARCHITECTURE

## 18.1 Acquisition Pipeline

```text
URL submitted
→ Platform detected
→ Source record created
→ Acquisition strategy selected
→ Metadata stored
→ Media or transcript acquired
→ Analysis run
→ Dossier saved
→ Patterns indexed
→ Mezie adaptation created
```

## 18.2 Apify Adapter

The adapter should support:

- Configured actor IDs
- Input validation
- Run tracking
- Budget enforcement
- Raw dataset preservation
- Cost logging
- Retry
- Source provenance

## 18.3 Copyright Rule

Store analysis and short excerpts where permitted. Avoid redistributing full third-party content unnecessarily.

---

# 19. TELEGRAM ARCHITECTURE

## 19.1 Integration Method

Use Telegram Bot API webhook in production and long polling during local development if preferred.

## 19.2 Authentication

- Allowlist Telegram user IDs
- Verify webhook secret
- Rate limit
- Log commands

## 19.3 Message Pipeline

```text
Telegram Update
→ Verify Sender
→ Store Raw Message
→ Download Attachment
→ Transcribe if Needed
→ Skill Router
→ Create Dashboard Records
→ Send Response
```

## 19.4 Supported Actions

- Capture idea
- Run research
- Submit benchmark
- Draft script
- Request review
- Show today
- Show week
- Approve action

## 19.5 Telegram Mini App

Future option. Telegram supports Mini Apps and bot-hosted web interfaces, but the MVP should use the Bot API and links into the PWA. citeturn179587search9turn179587search31

---

# 20. FRONTEND ARCHITECTURE

## 20.1 App Router

Use route groups:

```text
src/app/
├── (auth)/
├── (dashboard)/
│   ├── dashboard/
│   ├── ideas/
│   ├── calendar/
│   ├── pipeline/
│   ├── scripts/
│   ├── production/
│   ├── benchmarks/
│   ├── analytics/
│   ├── brand/
│   ├── proof/
│   ├── agent/
│   ├── assets/
│   └── settings/
└── api/
```

## 20.2 Data Fetching

- Server Components for initial reads where appropriate
- Client Components for interactive boards and editors
- TanStack Query for client cache and mutations
- SSE or WebSocket for job updates

## 20.3 State

Global client state:

- Sidebar
- Active filters
- Draft UI state
- Command palette
- Notifications

Server state remains in TanStack Query.

## 20.4 Forms

- React Hook Form
- Zod schemas shared through generated contracts

## 20.5 Editors

- TipTap for scripts, briefs, and documents
- JSON document structure plus rendered Markdown export

## 20.6 Drag and Drop

- DnD Kit for pipeline and calendar movement

## 20.7 Charts

- Recharts
- Server-generated export later

## 20.8 PWA

- Manifest
- Icons
- Standalone display
- Service worker
- Offline idea capture
- Background sync where safe
- Push notifications later

---

# 21. SEARCH ARCHITECTURE

## 21.1 Search Types

- Exact title
- Full-text
- Tags
- Filters
- Semantic
- Recent
- Command palette

## 21.2 Indexes

- PostgreSQL full-text
- pgvector
- Asset metadata
- Vault index
- Optional external search later

## 21.3 Search Permissions

Restricted records must not appear in unauthorized results.

---

# 22. ASSET PIPELINE

```text
Upload
→ Virus or type check
→ Hash
→ Duplicate check
→ Store original
→ Extract metadata
→ Generate preview
→ Tag
→ Index
→ Link
```

## Supported Processing

- Image thumbnails
- Video poster frames
- Audio waveform
- FFmpeg metadata
- Transcript linkage
- Orientation detection

---

# 23. ANALYTICS ARCHITECTURE

## 23.1 Ingestion Layers

Stage 1:

- Manual entry

Stage 2:

- CSV import

Stage 3:

- API connectors

## 23.2 Normalization

Normalize per platform:

- Views
- Impressions
- Reach
- Engagement
- Watch time
- Completion
- Saves
- Shares
- Follows

## 23.3 Insight Engine

The engine shall:

- Compare similar content
- Calculate normalized performance
- Detect patterns
- Generate hypotheses
- Create experiments
- Track confidence
- Avoid unsupported causal claims

---

# 24. APPROVAL ARCHITECTURE

## 24.1 Approval States

```text
not_required
pending
approved
rejected
expired
cancelled
```

## 24.2 Risk Levels

- Low
- Medium
- High
- Critical

## 24.3 Enforcement

All high-risk actions must check approval in backend code, not only the UI.

---

# 25. SECURITY ARCHITECTURE

## 25.1 Authentication

MVP options:

- Local password
- Magic link
- Auth.js-backed identity

## 25.2 Authorization

- Single user initially
- Permission framework retained for future roles

## 25.3 Secrets

- `.env` for local development
- Secret manager for cloud
- Never send secrets to model prompts
- Never write secrets to vault

## 25.4 Network

- HTTPS
- Secure cookies
- CSRF protection where applicable
- CORS allowlist
- Telegram webhook secret
- Rate limiting

## 25.5 Data

- Encryption at rest where supported
- Encrypted backups
- Restricted memory classification
- Audit logs
- Soft deletion

## 25.6 AI Safety

- Tool allowlists
- Output schema validation
- Prompt injection defenses for external content
- Source isolation
- Approval gates
- Cost limits
- Timeout and retry limits

---

# 26. OBSERVABILITY

## 26.1 Logs

- Structured JSON logs
- Request ID
- User ID
- Brand ID
- Agent run ID
- Job ID
- Skill
- Tool
- Cost
- Duration
- Status

## 26.2 Metrics

- API latency
- Error rate
- Queue depth
- Job duration
- Model cost
- Tool cost
- Token usage
- Retrieval hit rate
- Approval wait time
- Heartbeat success
- Vault sync failures

## 26.3 Tracing

Use OpenTelemetry when practical.

Trace:

- API request
- Agent run
- Skill steps
- Tool calls
- Database writes
- Memory writes
- Notifications

## 26.4 Error Reporting

- Sentry or equivalent
- User-safe error messages
- Detailed internal context

---

# 27. BACKUP AND DISASTER RECOVERY

## 27.1 Backup Targets

- PostgreSQL
- Obsidian vault
- Object storage
- Configuration
- Integration metadata

## 27.2 Schedule

- Daily incremental
- Weekly full
- Monthly retained checkpoint

## 27.3 Restore Test

Run monthly during MVP.

## 27.4 Recovery Objectives

Initial targets:

- RPO: 24 hours
- RTO: 4 hours

Improve for production.

---

# 28. TESTING STRATEGY

## 28.1 Unit Tests

- Scoring
- Status transitions
- Approval checks
- Schema validation
- Context ranking
- Cost calculations

## 28.2 Integration Tests

- Database
- Vault sync
- OpenAI adapter
- Telegram
- Apify
- Asset storage
- Queue

## 28.3 End-to-End Tests

Critical flows:

1. Dashboard idea to script
2. Telegram voice note to idea
3. Creator link to teardown
4. Script to production plan
5. Content status transitions
6. Manual heartbeat
7. Analytics import to insight
8. Canonical document approval
9. Backup and restore

## 28.4 Agent Evaluations

- Brand alignment
- Context correctness
- Fact preservation
- Hallucination resistance
- Approval compliance
- Financial-content safety
- Creator-copying prevention

## 28.5 Golden Fixtures

Maintain approved examples for:

- Builder Walk script
- LinkedIn post
- Creator teardown
- Daily brief
- Production plan
- Analytics insight
- Context pack

---

# 29. CI/CD

## Pipeline

```text
Lint
→ Type Check
→ Unit Tests
→ Integration Tests
→ Build
→ Security Scan
→ Database Migration Check
→ Deploy Preview
→ E2E Tests
→ Manual Approval
→ Production
```

## Branches

- main
- develop
- feature branches

## Deployment

- Preview per pull request
- Staging
- Production

---

# 30. CONFIGURATION

## Environment Variables

```text
DATABASE_URL
REDIS_URL
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_SECRET
TELEGRAM_ALLOWED_USER_IDS
APIFY_TOKEN
BRANDOS_VAULT_PATH
CREED_MEMORY_URL
OBJECT_STORAGE_ENDPOINT
OBJECT_STORAGE_BUCKET
OBJECT_STORAGE_ACCESS_KEY
OBJECT_STORAGE_SECRET_KEY
APP_BASE_URL
API_BASE_URL
ENCRYPTION_KEY
```

## Model Configuration

Stored in database or config:

```yaml
brand_quality_model: configurable
brand_fast_model: configurable
brand_vision_model: configurable
brand_transcription_model: configurable
brand_embedding_model: configurable
```

---

# 31. COST CONTROLS

- Daily model budget
- Weekly research budget
- Apify budget
- Maximum sources per run
- Maximum media size
- Model routing
- Cached context packs
- Cached source results
- Duplicate detection
- Batch processing
- Manual Deep Research approval

---

# 32. MIGRATION PATH TO MULTI-TENANT

The MVP shall include `brand_id` and `user_id` in core records.

Future additions:

- organizations
- memberships
- roles
- subscriptions
- usage limits
- tenant-scoped storage
- tenant-specific vaults
- tenant-specific model keys

Do not implement billing in MVP.

---

# 33. IMPLEMENTATION PHASES

## Phase 1 — Core Platform

- Repository
- Docker Compose
- Postgres
- Next.js shell
- FastAPI
- Auth
- Brand Library
- Ideas
- Pipeline
- Audit log

## Phase 2 — Agent Runtime

- OpenAI adapter
- Skill registry
- Router
- Context Packs
- Agent Console
- Run logging
- Approval service

## Phase 3 — Content Workflow

- Briefs
- Script Studio
- Hook Lab
- Calendar
- Production
- Assets
- Mobile PWA

## Phase 4 — Memory and Research

- Vault sync
- Embeddings
- Creator Intelligence
- Apify
- Heartbeat
- Telegram

## Phase 5 — Analytics and Proof

- Metrics
- CSV import
- Insights
- Experiments
- Case studies
- Proof manager

## Phase 6 — Hardening

- E2E tests
- Security
- Backups
- Performance
- Documentation
- Operational runbooks

---

# 34. ARCHITECTURE DECISIONS

## ADR-001: Modular Monolith

Chosen because:

- Single primary user
- Faster iteration
- Easier debugging
- Lower operating cost
- Clear future extraction boundaries

## ADR-002: PostgreSQL as Operational Source of Truth

Chosen because:

- Strong relational integrity
- JSONB
- Full-text
- pgvector
- Reliable migrations

## ADR-003: Dedicated Obsidian Vault

Chosen because:

- Human-readable memory
- Local ownership
- Existing CreedAI operating preference
- Easy audit and editing

## ADR-004: One Agent, Many Skills

Chosen because:

- Better context consistency
- Lower cost
- Fewer coordination failures
- Easier evaluation

## ADR-005: PWA Before Native App

Chosen because:

- One codebase
- Faster delivery
- Installable mobile experience
- Native wrapper remains possible later

## ADR-006: Human Approval Before Publishing

Chosen because:

- Brand and legal safety
- Financial-content sensitivity
- Early-stage trust
- Controlled learning

---

# 35. TECHNICAL ACCEPTANCE CRITERIA

The architecture is successfully implemented when:

1. All services run through one documented local command.
2. Database migrations apply cleanly.
3. Canonical files import into the Brand Library.
4. Vault sync is bidirectional with conflict handling.
5. Telegram creates dashboard records.
6. Agent runs use registered skills and typed outputs.
7. Every high-risk action enforces backend approval.
8. Heartbeat jobs are idempotent.
9. All model and tool costs are logged.
10. Critical workflows pass end-to-end tests.
11. Backup and restore pass.
12. PWA installs on desktop and phone.
13. API secrets never reach the client.
14. The UI receives live job updates.
15. External-source failures produce honest partial results.

---

# 36. FINAL ARCHITECTURE STATEMENT

Mezie Brand OS shall operate as a modular, local-first brand intelligence platform with a premium Next.js interface, a FastAPI intelligence backend, PostgreSQL and vector retrieval, a dedicated Obsidian vault, asynchronous research workers, a Telegram interface, and one governed Brand Director agent using versioned specialist skills.

The architecture must support the complete journey:

```text
Idea
→ Context
→ Research
→ Brief
→ Script
→ Production
→ Publication
→ Analytics
→ Learning
→ Memory
```

without losing founder identity, evidence, provenance, or human control.

---

**Technical Architecture Status:** Ready for database schema, API contracts, UX implementation, and Codex build prompt
