# Mezie Content Cycle Development Skill

## Purpose

Govern the full research-to-publication development cycle for recurring Mezie content.

Use this skill to convert brand strategy, founder context, business activity, audience needs,
creator intelligence, current developments, available evidence, production capacity, and platform
requirements into a controlled cycle of research, ideation, scoring, briefing, scripting,
creative direction, production planning, repurposing, publishing preparation, analytics review,
and learning records.

This skill generalizes the August content development framework into a reusable BrandOS capability
for monthly, weekly, quarterly, campaign, product-launch, brand-launch, event-led, reactive-news,
and evergreen-library content cycles.

## Triggers

- Build a content cycle
- Create a monthly content calendar
- Create a weekly publishing cycle
- Plan an August content calendar
- Build a campaign calendar
- Create a product-launch content plan
- Plan a founder-brand content sprint
- Build a quarterly editorial program
- Create a recurring content series
- Plan a reactive content window
- Create a cross-platform repurposing plan
- Build a research-to-publication pipeline
- Create a production batch plan
- Build creator-benchmark-informed content strategy

## Required Context

- Canonical Mezie brand positioning
- Personal brand and business-personal-brand integration rules
- Current content pillars and recurring series
- Audience personas, audience needs, objections, and desired transformations
- Current calendar, pipeline, production capacity, and active campaigns
- Founder stories, proof-of-work records, project activity, and available evidence
- Creator benchmark records and transferability boundaries
- Trend, market, platform, and research records
- Analytics, experiment history, and prior learning records
- Approval, financial-content, publishing, and sensitivity boundaries

## Tools and Dependencies

- Brand Memory and Vault
- Context Pack Builder
- Brand Strategy
- Audience Intelligence
- Creator Intelligence
- Trend Research
- Content Ideation
- Content Brief
- Hook Lab
- Scriptwriting
- Fact Checking
- Creative Direction
- Production Planning
- Platform Adaptation
- Caption and Social Copy
- Content Pipeline
- Calendar Orchestration
- Publishing Safety
- Analytics Review
- Content Experimentation
- Proof of Work

## Workflow

1. Lock the content cycle type, time period, goals, capacity, platforms, and required output package.
2. Retrieve canonical brand context and preserve the position: Mr. C. Mezie helps ambitious builders turn ideas, technology, and opportunity into systems, businesses, and ownership.
3. Preserve the signature operating idea: See the possibility. Build the system. Become the evidence.
4. Integrate the personal brand and business-personal-brand dimensions so the personal side explains the builder and the business side proves the builder.
5. Classify missing inputs and continue with explicit assumptions when the user has not supplied full context.
6. Run research before ideation: define questions, set the time window, collect evidence, classify opportunities, and create research records.
7. Classify every claim as verified fact, founder experience, founder interpretation, working hypothesis, strategic recommendation, creative device, or unverified signal.
8. Reject hallucinated founder experiences, fake analytics, invented benchmarks, unsupported statistics, copied creator expression, and unsupported authority claims.
9. Build the content architecture across pillar, series, content mode, production format, platform adaptation, objective, and experiment.
10. Generate ideas from brand-led, audience-led, evidence-led, market-led, and creator-led sources.
11. Score ideas for strategy, audience value, proof, originality, timeliness, feasibility, risk, and production fit.
12. Construct the content portfolio across the chosen cycle, balancing pillars, platforms, complexity classes, and production load.
13. Convert selected ideas into briefs with audience, thesis, proof, angle, hook direction, format, platform, CTA, risks, and evidence needs.
14. Develop hooks, scripts, creative direction, shot lists, B-roll plans, production batches, and platform-native adaptations.
15. Apply quality gates for strategic fit, authority, evidence, originality, audience value, script quality, production feasibility, platform fit, final review, and learning design.
16. Keep public publishing, external scheduling, financial claims, sensitive founder stories, canonical changes, paid acquisition, and outreach approval-gated.
17. Produce the final output package and register next actions in the dashboard, calendar, pipeline, memory, and analytics surfaces.
18. After publishing or testing, review 24-hour, 72-hour, and seven-day performance and write the learning record back to BrandOS memory.

## Required Outputs

- strategy_artifact
- research_artifact
- idea_bank
- scored_idea_matrix
- final_calendar
- content_briefs
- scripts
- creative_direction_files
- shot_lists
- b_roll_plans
- production_plan
- repurposing_matrix
- publishing_pack
- experiment_plan
- analytics_learning_record
- approvals_required
- dashboard_writes
- memory_writes

## Standard Output Envelope

```json
{
  "skill": "30_mezie_content_cycle_development",
  "status": "success|partial|blocked|failed",
  "summary": "string",
  "outputs": {
    "strategy_artifact": "skill-defined value",
    "research_artifact": "skill-defined value",
    "idea_bank": "skill-defined value",
    "scored_idea_matrix": "skill-defined value",
    "final_calendar": "skill-defined value",
    "content_briefs": "skill-defined value",
    "scripts": "skill-defined value",
    "creative_direction_files": "skill-defined value",
    "production_plan": "skill-defined value",
    "repurposing_matrix": "skill-defined value",
    "publishing_pack": "skill-defined value",
    "experiment_plan": "skill-defined value",
    "analytics_learning_record": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "dashboard_writes": [],
  "approvals_required": [],
  "warnings": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Require human approval before public publishing, public scheduling, external outreach, paid research, paid scraping, destructive deletion, or canonical brand changes.
- Require approval before treating a campaign calendar as a public commitment.
- Require approval before using sensitive founder stories, private client/project evidence, financial claims, investment claims, or authority claims that are not supported by current evidence.
- Allow low-risk internal planning writes, rough ideas, briefs, calendar planning blocks, and experiment proposals when they remain internal and reviewable.

## Memory Rules

- Preserve the full provenance chain from source input to research record, idea, brief, script, creative direction, production plan, adaptation, approval, publication, analytics, and learning record.
- Save assumptions and missing inputs as working notes rather than canonical strategy.
- Promote repeated learnings only after evidence, review, and approval.
- Store creator-benchmark influence as transferable mechanics, never copied wording, identity, or protected expression.
- Use the reference files in this folder when a task requires the full content-cycle doctrine or the originating August implementation.

## Failure Handling

- Return `blocked` when required approvals, evidence, permissions, or source material are missing.
- Return `partial` when enough context exists to produce strategy, research questions, assumptions, or a draft plan but not final production-ready artifacts.
- Do not invent missing founder experiences, analytics, examples, dates, external sources, or benchmark outcomes.
- If current research is unavailable, clearly label recommendations as working hypotheses and queue fact-checking or research next actions.
- If production capacity is unknown, produce a capacity-safe minimum viable plan and ask for confirmation before creating a heavier calendar.

## References

- `references/MEZIE_AUGUST_CONTENT_DEVELOPMENT_FRAMEWORK.md` is the originating August framework and should be read for detailed month-specific governance, pillar, series, mode, production, publishing, and learning rules.
- `references/MEZIE_CONTENT_CYCLE_DEVELOPMENT_SKILL.md` is the full downloaded reusable skill source.
- `references/SKILL_SOURCE.md` is the exact downloaded `SKILL.md` source file. It currently has the same SHA-256 content hash as `MEZIE_CONTENT_CYCLE_DEVELOPMENT_SKILL.md` and is preserved for provenance.
