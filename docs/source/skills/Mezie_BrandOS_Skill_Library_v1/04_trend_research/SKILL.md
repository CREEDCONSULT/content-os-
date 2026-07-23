# Trend Research Skill

## Purpose

Identify, score, and contextualize timely topics, platform formats, cultural conversations, and emerging opportunities relevant to the brand.

## Triggers

- What is trending?
- What should I talk about today?
- Run the heartbeat
- Find current topics
- Research platform shifts

## Required Context

- Brand pillars
- Audience
- Active campaigns
- Creator watchlist
- Trend scoring model
- Content calendar

## Tools and Dependencies

- Web search
- Platform search
- Google Trends
- News sources
- Creator Intelligence
- Analytics

## Workflow

1. Define the research window and topic scope.
2. Search multiple relevant sources.
3. Collect evidence and remove duplicates.
4. Score each trend for brand relevance, audience relevance, timeliness, evidence, originality potential, platform fit, shelf life, and feasibility.
5. Classify as Act Now, Research, Watch, Evergreen, Ignore, or Brand Risk.
6. Generate original Mezie angles.
7. Recommend calendar actions.

## Required Outputs

- trend_signals
- scores
- recommended_actions
- content_angles
- sources

## Standard Output Envelope

```json
{
  "skill": "04_trend_research",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "trend_signals": "skill-defined value",
    "scores": "skill-defined value",
    "recommended_actions": "skill-defined value",
    "content_angles": "skill-defined value",
    "sources": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- No approval required for research; approval required before calendar or publishing changes.

## Memory Rules

- Save trend records with date, freshness class, evidence, and expiry date.

## Failure Handling

- Never present a single-source observation as an established trend.

## Quality Checklist

- The output is specific to Mr. C. Mezie and the active BrandOS context.
- Facts, strategy, inference, and hypothesis are clearly separated.
- The output follows the approved brand voice and boundaries.
- Relevant records are linked rather than duplicated.
- Any uncertainty, missing evidence, or freshness issue is disclosed.
- No public, paid, destructive, or canonical action occurs without the required approval.
- The run is logged through the Agent Transparency skill.

## Implementation Notes

- This skill should be callable through the BrandOS Skill Router.
- Inputs and outputs should be validated with typed schemas.
- Context should be supplied through the Context Pack Builder rather than one giant prompt.
- Use configurable model aliases rather than hardcoded model names.
- Prefer deterministic tools and database actions for state changes.
