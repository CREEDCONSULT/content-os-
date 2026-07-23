# MEZIE BRANDOS SKILL LIBRARY

## Version 1.0

**Purpose:** Complete skill architecture for the Mezie BrandOS Brand Director Agent and supporting system.

## Operating Model

The MVP should use one Brand Director agent with specialized skills. The Skill Router selects the appropriate skill or skill chain. The Context Pack Builder retrieves the minimum relevant context. The Agent Transparency skill logs all meaningful runs. Public actions, paid actions above budget, sensitive stories, financial claims, and canonical strategy changes remain approval-gated.

## Skill Inventory

1. **BrandOS Skill Router** — `00_skill_router/SKILL.md`
   - Classify incoming requests, select the correct skill or skill chain, load the minimum relevant context, and enforce approval and safety rules.

2. **Brand Strategy Skill** — `01_brand_strategy/SKILL.md`
   - Evaluate and develop positioning, category ownership, audience focus, brand promise, differentiation, campaign strategy, and strategic coherence.

3. **Audience Intelligence Skill** — `02_audience_intelligence/SKILL.md`
   - Understand audience segments, questions, language, pain points, objections, and desired transformations.

4. **Creator Intelligence Skill** — `03_creator_intelligence/SKILL.md`
   - Analyze benchmark creators and content while extracting transferable mechanics without copying identity, wording, or protected expression.

5. **Trend Research Skill** — `04_trend_research/SKILL.md`
   - Identify, score, and contextualize timely topics, platform formats, cultural conversations, and emerging opportunities relevant to the brand.

6. **Daily Brand Intelligence Heartbeat Skill** — `05_daily_heartbeat/SKILL.md`
   - Run the scheduled daily research and update cycle that keeps BrandOS current.

7. **Content Ideation Skill** — `06_content_ideation/SKILL.md`
   - Turn raw thoughts, audience questions, trends, stories, and projects into scored content ideas.

8. **Content Brief Skill** — `07_content_brief/SKILL.md`
   - Convert an approved idea into a precise, platform-ready content brief before scripting.

9. **Platform Scriptwriting Skill** — `08_scriptwriting/SKILL.md`
   - Write original, brand-aligned scripts tailored to platform, format, audience, and production reality.

10. **Hook Lab Skill** — `09_hook_lab/SKILL.md`
   - Generate, classify, score, test, and preserve high-performing hooks.

11. **Founder Storytelling Skill** — `10_founder_storytelling/SKILL.md`
   - Retrieve, structure, and safely adapt founder experiences into public stories.

12. **Platform Adaptation Skill** — `11_platform_adaptation/SKILL.md`
   - Adapt one core idea into platform-native versions without losing message consistency.

13. **Creative Direction Skill** — `12_creative_direction/SKILL.md`
   - Translate a content concept into a coherent visual, sonic, emotional, and cinematic direction.

14. **Production Planning Skill** — `13_production_planning/SKILL.md`
   - Turn an approved script and creative direction into an executable shoot plan.

15. **Visual Review Skill** — `14_visual_review/SKILL.md`
   - Critique footage, thumbnails, lighting, wardrobe, backgrounds, graphics, and edited videos against brand and platform standards.

16. **Caption and Social Copy Skill** — `15_caption_copy/SKILL.md`
   - Create captions, post copy, CTAs, titles, descriptions, and supporting text for each platform.

17. **Financial Content Safety Skill** — `16_financial_content_safety/SKILL.md`
   - Ensure market, crypto, stock, ETF, and wealth content remains educational, evidence-based, and within approved boundaries.

18. **Research and Fact-Checking Skill** — `17_fact_checking/SKILL.md`
   - Verify claims, dates, statistics, quotations, platform changes, and current events before publication.

19. **Content Pipeline Management Skill** — `18_content_pipeline/SKILL.md`
   - Move content through the lifecycle while maintaining ownership, deadlines, blockers, and approvals.

20. **Editorial Calendar Orchestration Skill** — `19_calendar_orchestration/SKILL.md`
   - Build and maintain monthly, weekly, campaign, and platform schedules.

21. **Analytics and Learning Skill** — `20_analytics_review/SKILL.md`
   - Interpret content and platform performance, generate hypotheses, and recommend measurable next experiments.

22. **Content Experimentation Skill** — `21_experimentation/SKILL.md`
   - Design, track, and evaluate controlled content experiments.

23. **Proof-of-Work and Case Study Skill** — `22_proof_of_work/SKILL.md`
   - Identify, structure, document, and publish evidence that strengthens authority.

24. **Brand Asset Management Skill** — `23_asset_management/SKILL.md`
   - Ingest, classify, tag, retrieve, and connect visual, audio, video, and document assets.

25. **Telegram Capture and Command Skill** — `24_telegram_capture/SKILL.md`
   - Convert Telegram text, links, images, files, and voice notes into structured BrandOS records and workflows.

26. **Brand Memory and Vault Skill** — `25_brand_memory/SKILL.md`
   - Write, retrieve, promote, archive, and govern BrandOS knowledge across the dedicated Obsidian vault and database.

27. **Context Pack Builder Skill** — `26_context_pack_builder/SKILL.md`
   - Assemble concise task-specific context from the full BrandOS memory without overloading model prompts.

28. **Agent Transparency and Run Logging Skill** — `27_agent_transparency/SKILL.md`
   - Make every important agent action explainable, reviewable, and auditable.

29. **Publishing and Approval Safety Skill** — `28_publishing_safety/SKILL.md`
   - Control final publishing actions and enforce platform, legal, brand, and permission checks.

30. **General Brand Assistant Skill** — `29_general_brand_assistant/SKILL.md`
   - Handle low-risk requests that do not require a specialist workflow while preserving brand context and routing learnings.

## Core Execution Chain

```text
User / Telegram / Heartbeat
        ↓
Skill Router
        ↓
Context Pack Builder
        ↓
One or more Specialist Skills
        ↓
Brand Memory + Dashboard Writes
        ↓
Agent Transparency Log
        ↓
Human Approval where required
```

## Recommended MVP Skill Set

Implement first:

- BrandOS Skill Router
- Brand Strategy
- Creator Intelligence
- Trend Research
- Daily Heartbeat
- Content Ideation
- Content Brief
- Scriptwriting
- Hook Lab
- Creative Direction
- Production Planning
- Content Pipeline
- Calendar Orchestration
- Telegram Capture
- Brand Memory and Vault
- Context Pack Builder
- Agent Transparency

## Phase 2 Skills

- Audience Intelligence
- Founder Storytelling
- Platform Adaptation
- Visual Review
- Caption and Social Copy
- Financial Content Safety
- Fact Checking
- Analytics Review
- Experimentation
- Proof of Work
- Asset Management
- Publishing Safety

## Canonical Approval Gates

Human approval is required for:

- Canonical positioning, audience, values, voice, or boundary changes
- Public publishing or scheduling
- High-risk financial content
- Sensitive founder stories
- Client-confidential proof
- Paid research or scraping above budget
- External outreach
- Destructive deletion

## Memory Promotion Model

```text
Raw Observation
→ Working Hypothesis
→ Repeated Pattern
→ Tested Insight
→ Approved Brand Learning
→ Canonical Principle
```