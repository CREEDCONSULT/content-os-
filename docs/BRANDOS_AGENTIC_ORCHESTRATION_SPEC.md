# BrandOS Agentic Orchestration Specification

Status: accepted target architecture; Phase 1 implemented, Phase 2 backend slice implemented  
Owner: BrandOS platform  
Created: 2026-08-03  
Last updated: 2026-08-03  
Related docs:

- [AGENT_RUNTIME.md](AGENT_RUNTIME.md)
- [BRANDOS_MEMORY_GRAPH_SPEC.md](BRANDOS_MEMORY_GRAPH_SPEC.md)
- [MEMORY_AND_VAULT.md](MEMORY_AND_VAULT.md)
- [API.md](API.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [HUMAN_ACTION_QUEUE.md](HUMAN_ACTION_QUEUE.md)

## 1. Executive decision

BrandOS should become agentic-first.

The dashboard should remain the clean command center and source-of-truth surface.
Telegram and dashboard chat should become the conversational rough-work surfaces
where the founder brainstorms, sends links, drops voice notes, asks questions,
plans content, and gives approvals.

The core change is this:

```text
Telegram and dashboard chat should not only ingest.
They should converse, reason, call tools, propose writes, ask follow-up questions,
and then route approved outcomes into the dashboard, vault, and memory graph.
```

BrandOS already has enough structural foundation to support this:

- authenticated dashboard;
- Telegram webhook and message ledger;
- agent runtime and skill registry;
- OpenAI Responses provider adapter;
- context packs;
- memory/vault system;
- memory graph;
- idea, content, script, calendar, production, benchmark, analytics, proof, and
  approval modules.

The missing layer is a conversational orchestration layer that connects those
modules into one operating agent.

## 2. Product goal

The goal is not to replace the founder's creativity.

The goal is to remove the operational strain around:

- remembering;
- organizing;
- researching;
- comparing creators;
- planning content;
- turning ideas into scripts;
- creating production instructions;
- updating the calendar;
- managing approvals;
- preserving decisions;
- preparing assets;
- creating publish-ready drafts.

The founder should be able to talk naturally:

> "This creator's latest video structure is good. Study this, compare it with our
> Build pillar, and give me three Mezie-style adaptations."

BrandOS should respond conversationally, use the right tools, show what it found,
ask what is missing, and then propose dashboard actions:

- save benchmark;
- update creator profile;
- create idea;
- create script brief;
- schedule draft;
- add research note;
- link all of it into the memory graph.

## 3. Current-state diagnosis

### What works today

| Capability | Current state |
|---|---|
| Telegram webhook | Verifies secret/sender and records messages |
| Telegram capture | Can save ideas, status checks, and benchmark URL stubs |
| Agent runtime | Routes intents to persisted skill definitions |
| OpenAI provider | Server-side Responses API adapter exists and uses structured output |
| Skills | 30 BrandOS skill definitions are imported |
| Context packs | Canonical documents and memory records are loaded into runs |
| Memory graph | Entities, edges, graph extraction, search, and neighborhood API exist |
| Benchmark module | Creator and benchmark records exist |
| Calendar | Internal capacity/scheduling records exist |
| Publishing safety | Public publishing remains approval-gated/unavailable |

### What does not work deeply enough yet

| Gap | Why it matters |
|---|---|
| Dashboard does not yet expose a rich planning chat UI | Desk-side planning still lacks a natural command interface |
| Proposed-action UI is not built | Safe/risky proposals exist in the API but need a human-friendly dashboard review surface |
| Only one safe write executor exists | `create_rough_idea` works; richer content, calendar, document, research, and media tools are deferred |
| Research tools are not live/orchestrated | The agent cannot reliably study creators, trends, or platform signals |
| Creator watchlist is seeded with examples, not the founder's real preferred creators | Benchmarks cannot reflect the actual taste graph |
| Context packs do not yet use graph traversal deeply | The new memory graph is not fully feeding the agent |
| Publishing is not integrated | Drafting can happen, but scheduling/posting must remain a future gated adapter |
| AI avatar/visual production is not represented as a first-class workflow | Avatar series, AI counterparts, and visual prompts need a structured content pipeline |

## 4. Architecture principle

BrandOS should own the brain.

Hermes, Telegram, OpenAI, Apify, and publishing services are adapters or harnesses.
They must not become the canonical source of truth.

```text
BrandOS API
  owns: database, approvals, memory graph, dashboard state, tool contracts

Telegram
  owns: lightweight conversational channel

Dashboard chat
  owns: focused planning and review UX

Hermes
  owns: optional local conversational harness/gateway

OpenAI
  owns: model reasoning, tool calling, multimodal generation/transcription

External tools
  own: research, scraping, posting, calendars, storage, media generation
```

## 5. Recommended high-level flow

```text
Telegram / Dashboard Chat
        |
        v
Conversation Orchestrator
        |
        +--> classify intent
        +--> load conversation state
        +--> retrieve context pack
        +--> traverse memory graph
        +--> select skills and tools
        |
        v
Brand Director Agent
        |
        +--> Research Agent
        +--> Creator Intelligence Agent
        +--> Content Strategy Agent
        +--> Script Studio Agent
        +--> Production Agent
        +--> Calendar Agent
        +--> Publishing Safety Agent
        +--> Memory Librarian Agent
        |
        v
Tool Execution Layer
        |
        +--> read-only tools execute directly
        +--> safe writes execute with audit trail
        +--> risky writes create approvals
        +--> external/paid tools require budget and config
        |
        v
Dashboard + Memory Graph + Vault + Telegram Reply
```

## 6. OpenAI integration stance

The current BrandOS provider uses the OpenAI Responses API directly. That is a
good starting point because BrandOS already owns the runtime loop, policy checks,
approvals, and database writes.

Use this progression:

1. **Responses API directly** for the next implementation slice.
   - Best when BrandOS controls the loop and wants strict tool policy.
   - Fits the existing `OpenAIResponsesProvider`.
2. **Agents SDK later** when BrandOS needs managed sessions, tracing, handoffs,
   guardrails, and resumable approval flows.
   - Useful once the tool catalog is stable.
   - Especially useful for specialist agents and long-running workflows.
3. **Realtime API later** for browser voice agents and low-latency dashboard
   voice sessions.
   - Dashboard voice should use browser WebRTC.
   - Server-side audio pipelines can use WebSockets.
   - Telegram voice notes should start with transcription, not full realtime
     speech-to-speech.

The first version should be manager-style orchestration:

```text
Brand Director = central conversational manager
Specialists = tools/subroutines called by the manager
```

Avoid starting with a fully decentralized swarm. It will be harder to audit,
harder to approve, and harder to keep aligned with BrandOS state.

## 7. Hermes integration stance

Hermes can be valuable, but it should not be merged blindly into BrandOS.

Recommended relationship:

```text
Hermes = optional harness/gateway
BrandOS = product brain and source of truth
```

### Approved Hermes use cases

- local Telegram conversational harness;
- model-provider gateway;
- experimental agent runtime;
- voice/chat shell;
- bridge for local tools that should not live in Railway;
- fallback path for NVIDIA NIM or other local provider experiments.

### Disallowed Hermes use cases

- do not make Hermes the canonical BrandOS database;
- do not point BrandOS at the existing CreedAI vault;
- do not leak Telegram bot tokens into the Hermes backend process;
- do not reuse old profiles/ports without live inspection;
- do not connect to CreedAI memory as writable state.

### Integration pattern

Use a clean BrandOS-specific Hermes profile if needed:

```text
Telegram
  -> BrandOS Telegram webhook
  -> BrandOS Conversation Orchestrator
  -> optional Hermes harness call
  -> BrandOS tools and approvals
  -> Telegram sendMessage reply
```

Alternative local-only experiment:

```text
Telegram
  -> Hermes Telegram listener
  -> BrandOS API tool calls
  -> BrandOS database/dashboard
```

The preferred production path is the first one because it keeps BrandOS in
control of security, audit, approvals, and dashboard writes.

## 8. Conversation data model

Add durable conversation state.

### `conversation_sessions`

Purpose: one brainstorming/planning thread across Telegram, dashboard chat, API,
or voice.

Suggested fields:

```text
id
brand_id
channel                  telegram|dashboard|voice|api
external_thread_id        telegram chat id, dashboard session id, etc.
title
status                   active|paused|resolved|archived
current_intent
active_agent             brand_director|research|script|calendar|...
memory_scope             rough|working|canonical_candidate
last_message_at
summary
open_questions
proposed_action_count
approval_count
is_demo
created_at
updated_at
```

### `conversation_messages`

Purpose: complete audit trail of founder messages, agent replies, tool summaries,
and handoffs.

Suggested fields:

```text
id
brand_id
session_id
channel
sender_type              user|agent|tool|system
sender_id
message_type             text|voice|image|file|link|tool_result|approval
content_text
content_json
source_reference
telegram_update_id
telegram_message_id
attachment_ids
agent_run_id
sensitivity
status                   received|processing|responded|failed|archived
created_at
updated_at
```

### `agent_tool_calls`

Purpose: transparent record of every tool the agent requested or executed.

Suggested fields:

```text
id
brand_id
session_id
agent_run_id
tool_name
tool_type                read|safe_write|approval_write|external|paid|publish
input_json
output_json
status                   proposed|running|completed|blocked|failed
cost_estimate
approval_id
error
created_at
updated_at
```

### `proposed_dashboard_actions`

Purpose: actions the agent wants to take on the dashboard.

Suggested fields:

```text
id
brand_id
session_id
agent_run_id
action_type              create_idea|update_idea|create_brief|schedule_event|...
target_type
target_id
payload
rationale
risk_level               low|medium|high|critical
status                   proposed|approved|executed|rejected|expired
approval_id
executed_at
created_at
updated_at
```

## 9. Telegram behavior

Telegram should have three lanes.

### Lane A: fast conversational reply

Use for ordinary messages, brainstorming, quick questions, rough thoughts, and
follow-up clarification.

Flow:

```text
receive Telegram update
verify sender and webhook secret
persist raw message
open/find conversation session
call conversation orchestrator
send natural Telegram reply
persist agent response
queue any slow work
```

The Telegram reply should sound like the Brand Director, not a database receipt.

Bad:

```text
Idea captured. Open the Ideas Inbox to score it.
```

Good:

```text
I see the angle: you are circling a "builder discipline vs motivation" post.
I saved the raw idea. Before I turn it into a script, do you want it to lean more
personal-story, teaching thread, or talking-head video?
```

### Lane B: command capture

Use slash commands for deliberate actions:

```text
/idea
/benchmark
/watch
/research
/script
/calendar
/status
/approve
```

Commands should still answer conversationally, but they can skip some ambiguity.

### Lane C: slow work queue

Use for research, file analysis, creator review, long script generation, visual
asset planning, and publishing preparation.

Telegram should acknowledge quickly:

```text
Got it. I’m going to study this creator, pull the reusable mechanics, and save a
benchmark draft. I’ll ping you when the teardown is ready.
```

Then the background job updates:

- dashboard record;
- conversation session;
- memory graph;
- Telegram follow-up reply.

## 10. Dashboard chat behavior

Dashboard chat should use the same conversation orchestrator as Telegram.

Primary locations:

```text
/agent
/ideas/:id/agent
/studio/:script_id/agent
/calendar/agent
/benchmarks/agent
/memory/agent
```

Dashboard chat should support:

- live agent messages;
- context chips showing loaded memory/skills/tools;
- proposed dashboard writes;
- approval buttons;
- “apply safe writes” button;
- “send to Telegram” handoff;
- source/provenance drawer;
- context pack preview;
- memory graph neighborhood preview.

The founder should be able to ask:

> Plan my next 30 days of content from the Build and Leverage pillars. Use my
> benchmark creators, avoid finance advice, and give me 12 posts, 4 scripts, and
> 2 AI-avatar experiments.

The system should produce:

- a draft 30-day plan;
- content items;
- scripts or brief stubs;
- calendar events;
- approvals for major schedule changes;
- memory graph links.

## 11. Tool execution policy

Classify every tool into one of five classes.

| Tool class | Examples | Execution rule |
|---|---|---|
| Read-only | search memory, list ideas, inspect calendar, get creator profile | execute directly |
| Safe write | create rough idea, save working note, create draft benchmark | execute directly with audit |
| Approval write | schedule content, promote canonical memory, major campaign plan | require approval |
| External/paid | Apify, web research, paid model-heavy run, media generation | require config and budget rules |
| Public action | publish post, send outreach, post externally | require explicit approval and enabled adapter |

The agent should never claim an action happened until the tool layer confirms it.

## 12. BrandOS tool catalog

The agent should receive a small, typed tool catalog.

### Read tools

```text
search_memory
search_graph
get_graph_neighborhood
list_ideas
get_idea
list_content_items
get_content_item
list_creators
get_creator
list_benchmarks
get_calendar_capacity
list_calendar_events
get_dashboard_summary
list_pending_approvals
```

### Safe write tools

```text
create_rough_idea
create_working_memory_note
create_creator_watch_candidate
create_benchmark_url_stub
create_script_draft
create_content_brief_draft
create_proposed_dashboard_action
link_graph_nodes
```

### Approval-gated tools

```text
schedule_calendar_event
move_content_to_ready_to_publish
approve_script_version
promote_memory_to_canonical
create_campaign_commitment
use_sensitive_founder_story
run_paid_research
publish_content
send_external_message
```

## 13. Research methodology

Research should be structured, not vibes.

Every research run should produce:

```text
research_question
source_plan
sources_checked
source_quality
what_changed
relevance_to_mezie
candidate_content_angles
benchmark_links
risks_or_noise
confidence
freshness_date
suggested_dashboard_actions
memory_writes
```

Research types:

| Type | Purpose |
|---|---|
| Creator review | Study a creator's content for reusable mechanics |
| Platform trend scan | Review what formats/topics are moving on a platform |
| Topic research | Understand a content topic before scripting |
| Proof research | Find supporting evidence for a claim |
| Competitor/peer review | Compare positioning and content systems |
| Production research | Gather visual, editing, format, or avatar references |

Research must distinguish:

- observed fact;
- source claim;
- model inference;
- founder preference;
- Mezie adaptation;
- hypothesis;
- publication-safe claim.

## 14. Creator benchmark system

The benchmark system must start from the founder's real taste graph.

The founder should be able to say:

```text
/watch https://youtube.com/@creator because I like how he explains complex systems
```

The agent should ask:

```text
What do you want me to watch in this creator: hooks, structure, voice, visuals,
editing, storytelling, or offers?
```

Creator records should include:

```text
name
platform
profile_url
why_founder_likes_them
watch_dimensions
signature_strengths
content_pillars
formats
voice_patterns
hook_patterns
story_patterns
visual_patterns
editing_patterns
protected_identity_boundaries
mezie_adaptation_rules
last_reviewed_at
review_cadence
```

Benchmark output should never say “copy this.” It should say:

```text
Reusable mechanic:
Mezie-native adaptation:
What to avoid:
Evidence:
Confidence:
Suggested content:
```

## 15. Content and avatar production system

BrandOS should support four content production modes:

| Mode | Description |
|---|---|
| Founder-recorded | talking-head, walk-and-talk, direct camera, documentary clips |
| AI-assisted visual | founder-led script with generated visuals/B-roll |
| AI-avatar | controlled avatar delivers scripted content |
| AI counterpart series | branded AI characters/counterparts participate in recurring content |

Add first-class concepts:

```text
avatar_profiles
visual_style_profiles
scene_templates
ai_counterpart_profiles
media_generation_jobs
```

Avatar/counterpart records should include:

```text
name
role_in_brand
voice_rules
visual_rules
allowed_topics
forbidden_topics
relationship_to_founder
disclosure_policy
prompt_template
sample_scripts
review_required
```

Publishing must clearly disclose AI-generated or AI-assisted media when required
by platform policy, brand ethics, or audience trust.

## 16. Publishing and scheduling

Publishing should be built in stages.

### Stage 1: draft-only

The agent can prepare:

- platform post text;
- captions;
- thumbnails/prompts;
- schedule recommendations;
- approval package.

### Stage 2: internal scheduling

The agent can create internal calendar events and pipeline states after approval.

### Stage 3: external scheduler integration

Connect to a scheduler or platform API.

The adapter must record:

- target platform;
- post body;
- asset ids;
- scheduled time;
- approval id;
- platform response;
- error state;
- final URL when published.

### Stage 4: direct publishing

Direct publishing is allowed only when:

- the adapter is configured;
- the target platform is approved;
- rights checks pass;
- sensitive-story checks pass;
- proof checks pass where needed;
- the founder explicitly approves the action.

## 17. Skill-folder roadmap

The existing skill library is a strong base. The next phase should add or deepen
these skill folders:

```text
30_conversation_orchestrator
31_tool_execution_policy
32_dashboard_operator
33_creator_watchlist_manager
34_research_methodology
35_telegram_conversation
36_dashboard_chat
37_avatar_content_strategy
38_ai_visual_direction
39_media_generation_prompting
40_publishing_scheduler
41_hermes_harness_adapter
42_brandos_mcp_tools
```

Each skill should define:

- trigger phrases;
- required context;
- allowed tools;
- output envelope;
- memory writes;
- dashboard writes;
- approval rules;
- failure behavior;
- examples.

## 18. MCP and tool-server direction

BrandOS should eventually expose its own tool server.

Purpose:

- allow Hermes to call BrandOS safely;
- allow local agents to inspect BrandOS state;
- allow external agent surfaces to use BrandOS tools without database access;
- keep approvals centralized in BrandOS.

First tool server surface:

```text
brandos.search
brandos.memory.search
brandos.memory.graph
brandos.idea.create
brandos.idea.update
brandos.creator.watch
brandos.benchmark.create
brandos.script.create_draft
brandos.calendar.propose
brandos.approval.create
brandos.action.execute_safe
```

The MCP/tool server should never expose raw credentials or allow public
publishing without approval.

## 19. Implementation phases

### Phase 1: conversational foundation

Deliverables:

- `conversation_sessions`;
- `conversation_messages`;
- Telegram session mapping;
- dashboard chat API;
- natural conversational Telegram replies;
- agent runtime called from Telegram;
- idempotent message handling;
- tests for conversational capture and reply.

### Phase 2: proposed actions and safe writes

Deliverables:

- `proposed_dashboard_actions` — implemented for the backend API;
- tool-call ledger — implemented for safe execution and blocked approval gates;
- safe write executor — implemented for `create_rough_idea`;
- approval-gated executor — implemented for known risky action proposals;
- dashboard UI for proposed writes;
- agent output proposal bridge recognizes `record_type="idea"` and
  `action="create_rough_idea"` without silently completing the write.

### Phase 3: memory graph context

Deliverables:

- context pack builder uses graph neighborhood;
- conversation summaries saved into memory;
- rough notes remain separate from canonical memory;
- useful context packs linked back to successful outputs.

### Phase 4: creator benchmark intelligence

Deliverables:

- real creator watchlist onboarding;
- Telegram `/watch` flow;
- creator review dimensions;
- benchmark teardown jobs;
- Mezie adaptation outputs;
- graph links from creators to pillars, ideas, scripts, and content.

### Phase 5: research engine

Deliverables:

- research run model;
- source ledger;
- Apify adapter if approved;
- web/source retrieval if configured;
- topic/creator/platform research workflows;
- dashboard research queue.

### Phase 6: content planning and calendar orchestration

Deliverables:

- 30-day content planner;
- campaign planner;
- calendar proposal generator;
- approval gate for major schedule changes;
- pipeline record creation from approved plans.

### Phase 7: AI avatar and media production

Deliverables:

- avatar profile model;
- visual style profile model;
- AI counterpart profile model;
- prompt packs for talking-head, avatar, B-roll, visual essays, and scene design;
- media generation job ledger;
- review/approval workflow.

### Phase 8: publishing adapter

Deliverables:

- draft-to-scheduler adapter;
- platform capability matrix;
- approval package;
- publish audit;
- rollback/error handling.

### Phase 9: Hermes harness adapter

Deliverables:

- isolated BrandOS Hermes profile;
- stateless loopback smoke;
- BrandOS tool server contract;
- no credential leakage;
- local-only fallback mode;
- clear distinction between Hermes harness and BrandOS source of truth.

## 20. First implementation slice

Build this first:

```text
Conversation Foundation v1
```

Scope:

1. Add conversation tables.
2. Add conversation service.
3. Route Telegram text messages into the BrandOS agent runtime.
4. Send outbound Telegram replies using the Bot API.
5. Preserve the raw Telegram message.
6. Persist the agent response.
7. Do not execute risky writes.
8. Convert explicit safe rough-idea suggestions into proposed actions; execute
   only through the action executor.
9. Add dashboard route to inspect conversations.
10. Add tests.

Why first:

- It immediately fixes the bot feeling non-conversational.
- It reuses the existing agent runtime.
- It does not require external research yet.
- It gives the dashboard a conversation ledger.
- It creates the foundation for tool use and Hermes later.

Implemented on 2026-08-03:

- `conversation_sessions`;
- `conversation_messages`;
- dashboard/API conversation turn route;
- authenticated session/message inspection routes;
- Telegram ordinary text routed to BrandOS agent runtime;
- `/idea` remains immediate rough idea creation plus agent response;
- benchmark/link captures route through the conversation lane when valid;
- Telegram Bot API outbound reply adapter with safe test/missing-token skip;
- regression tests for dashboard and Telegram conversation turns.

Phase 2 backend slice implemented on 2026-08-03:

- `agent_tool_calls`;
- `proposed_dashboard_actions`;
- `/api/v1/actions/proposals`;
- `/api/v1/actions/proposals/{id}/execute`;
- `/api/v1/actions/tool-calls`;
- safe `create_rough_idea` executor;
- approval-gated public/publishing/canonical/sensitive/paid/external action
  proposals;
- conversation-to-proposed-action bridge for recognized agent write proposals;
- regression tests for safe execution and risky approval gating.

## 21. Acceptance criteria

The next phase is working when:

- a Telegram message gets a natural conversational reply;
- the reply is produced by the BrandOS agent runtime;
- the message and reply are stored in a conversation session;
- the agent can load memory/context;
- the agent can propose a dashboard write;
- safe writes are auditable;
- risky writes require approval;
- dashboard/API users can inspect the conversation and proposed actions;
- creator benchmark links can enter as rough records;
- no external publishing happens silently;
- Hermes remains optional and isolated.

## 22. Strategic conclusion

This is the correct next evolution:

```text
BrandOS should become a conversational operating system for the brand.
```

Telegram is the messy creative room.

Dashboard chat is the focused planning room.

The dashboard is the command center.

The memory graph is the institutional brain.

The agent runtime is the operator.

Hermes is a possible harness, not the owner.

Publishing and external research are powerful, but they must come after
conversation, memory, tools, and approvals are structurally sound.
