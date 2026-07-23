# Source Document Inventory

Inventory date: 2026-07-23
Implementation repository: `C:\Users\daunt\OneDrive\Desktop\content creation os\mezie-brandos`

The original files are preserved byte-for-byte under `docs/source`. Requirements are not silently discarded; conflicts are captured in `docs/DECISION_LOG.md`.

| Source | Repository path | Purpose | Status | Major requirements | Modules affected | Conflicts or ambiguity |
|---|---|---|---|---|---|---|
| Personal Brand Positioning Architecture v1 | `docs/source/core/Mr_C_Mezie_Personal_Brand_Positioning_Architecture_v1.md` | Founder-facing public positioning and brand boundaries | Canonical brand strategy | Builder Intelligence category; primary and secondary audiences; six pillars; voice; platform roles; proof and financial boundaries; signature line | Brand Intelligence, context packs, seed data, scripts, safety, analytics | References a Founder Identity OS that was not supplied; older content allocation differs from the execution handbook |
| Personal Brand Execution Handbook v1 | `docs/source/brand-execution/Mr_C_Mezie_Personal_Brand_Execution_Handbook_v1.md` | Operationalizes positioning for August–December 2026 | Canonical execution strategy | Personas; pillars and series; platform rhythms; visual/verbal identity; story safety; five-month plan; proof roadmap | Seed data, calendar, ideas, scripts, production, proof, safety | Recommends Build 30% and Create 10%, unlike the positioning document's 35% and 5% |
| Execution System supporting files | `docs/source/brand-execution/Mr_C_Mezie_Personal_Brand_Execution_System/` | Ten independently retrievable brand and execution records | Canonical supporting records | Audience, series, platform playbooks, Instagram, LinkedIn, visual identity, voice, founder stories, operating cadence, proof | Brand document import and task-specific context retrieval | Duplicates handbook content intentionally; import must link documents rather than pretend they are independent new strategies |
| Brand Engineering Harness Product Architecture v1 | `docs/source/core/Mr_C_Mezie_Brand_Engineering_Harness_Product_Architecture_v1.md` | Early product definition and module map | Supporting product architecture | One agent/many skills; local-first web/PWA; Telegram; full content lifecycle; production and analytics | All product modules | Later PRD and technical specification are more implementation-specific |
| Autonomous Intelligence, Memory, Heartbeat Architecture v1 | `docs/source/core/Mezie_BrandOS_Autonomous_Intelligence_Memory_Heartbeat_Architecture_v1.md` | Required amendment for persistent research, memory, and learning | Canonical architecture amendment | Manual-first heartbeat; budget control; dedicated vault; memory promotion; creator watchlist; provenance; partial-result honesty | Heartbeat, memory, analytics, benchmarks, agent logs | Suggests a default external vault path that requires founder confirmation |
| Product Requirements Document v1 | `docs/source/core/Mezie_BrandOS_Product_Requirements_Document_v1.md` | Product behavior, scope, and acceptance criteria | Canonical product baseline | 22 modules; desktop/PWA/Telegram; approval queue; search; performance, accessibility, security, and release criteria | All product modules and QA | Very broad MVP; vertical slices are required to avoid placeholder-only coverage |
| Technical Architecture Specification v1 | `docs/source/core/Mezie_BrandOS_Technical_Architecture_Specification_v1.md` | Repository, data, API, job, agent, storage, and deployment architecture | Canonical implementation architecture | Modular monolith; Next.js + FastAPI; PostgreSQL/pgvector; Alembic; typed APIs; DB-backed jobs; provider adapters; SSE/WebSocket; Docker Compose | Entire repository | Requires Python 3.12+, while the host has 3.11.9; Docker can use 3.12 |
| UI/UX Frontend Development Plan v2 | `docs/source/core/Mezie_BrandOS_UIUX_Frontend_Development_Plan_v2.md` | Most recent screen and design-system specification | Canonical frontend baseline | Obsidian/charcoal/gold tokens; compact density; shell; page anatomy; responsive mobile companion; accessibility | Web app and design system | Simplified five-column pipeline conflicts with the PRD's full 15-stage lifecycle |
| Complete Skill Handbook v1 | `docs/source/skills/Mezie_BrandOS_Complete_Skill_Handbook_v1.md` | Consolidated agent-skill specification | Canonical agent behavior | Global envelopes; 30 skills; workflows; approvals; memory; failure behavior; quality rules | Agent runtime, schemas, tests, docs | Handbook prose lacks explicit cost class, timeout, and model-profile values required by the later build mandate |
| Skill Library v1 | `docs/source/skills/Mezie_BrandOS_Skill_Library_v1/` | Individual runtime-ready skill source files and global contracts | Canonical skill source | Skill router, context packs, transparency, content/research/production/analytics/safety skills | Agent runtime and skill registry | Individual Markdown files require compilation into typed runtime manifests |
| Approved dashboard suite mockup | `docs/source/ui-mockups/ChatGPT Image Jul 23, 2026, 02_22_47 PM.png` | Visual coverage for desktop modules, mobile companion, and Telegram | Canonical visual reference | Premium density, navigation, gold actions, colored data accents, page compositions | All frontend screens | Contains illustrative metrics and integration states that must be marked demo or replaced by live status |
| Approved dashboard detail mockup | `docs/source/ui-mockups/ChatGPT Image Jul 23, 2026, 02_22_54 PM.png` | High-detail Command Center, Calendar, Script Studio, and Analytics layouts | Canonical visual reference | Shell proportions, card hierarchy, chart density, action placement | Dashboard, calendar, scripts, analytics | Illustrative date and metric values are not factual product data |
| User flows overview mockup | `docs/source/ui-mockups/ChatGPT Image Jul 23, 2026, 02_06_32 PM.png` | Cross-interface workflow and system-access map | Supporting flow reference | Idea-to-publish, heartbeat, Telegram, analytics learning, multi-interface access | Workflow, agent, Telegram, analytics | Includes publishing/distribution as a future flow; autonomous publishing is explicitly excluded from MVP |

## Referenced but missing

| Missing source | Impact | Current handling |
|---|---|---|
| Founder Identity OS v1 | The positioning document cites it as an upstream source | Positioning Architecture and Execution Handbook are treated as the available canonical identity derivatives; confirmation remains in the human-action queue |
| Standalone UI/UX Component Design Specification | The build mandate names it, but no separate file was supplied | UI/UX Frontend Plan v2 and the approved images provide the working component specification |
| Standalone Database Schema | Technical specification lists entities but no executable schema was supplied | The implementation creates and documents an Alembic-managed schema |

## Precedence

1. Latest implementation-specific document.
2. Product Requirements Document for observable behavior.
3. Technical Architecture Specification for system boundaries.
4. UI/UX Frontend Plan v2 and images for interface decisions.
5. Execution Handbook for brand operating defaults.
6. Positioning Architecture for canonical identity and public boundaries.
