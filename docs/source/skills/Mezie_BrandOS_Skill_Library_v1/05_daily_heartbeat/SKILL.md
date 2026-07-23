# Daily Brand Intelligence Heartbeat Skill

## Purpose

Run the scheduled daily research and update cycle that keeps BrandOS current.

## Triggers

- Daily scheduler
- Manual Run Daily Intelligence command

## Required Context

- Brand context pack
- Creator watchlist
- Current calendar
- Active campaigns
- Recent analytics
- Research budget

## Tools and Dependencies

- Trend Research
- Creator Intelligence
- Analytics Review
- Vault
- Telegram

## Workflow

1. Load current brand priorities.
2. Review Tier 1 creator activity.
3. Scan relevant current topics and platform changes.
4. Detect repeated, new, declining, and risky patterns.
5. Generate up to five content opportunities.
6. Create one priority recommendation.
7. Write the Daily Intelligence Brief.
8. Update working memory and dashboard records.
9. Send concise Telegram summary.

## Required Outputs

- daily_brief
- creator_updates
- trend_updates
- idea_candidates
- recommended_action

## Standard Output Envelope

```json
{
  "skill": "05_daily_heartbeat",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "daily_brief": "skill-defined value",
    "creator_updates": "skill-defined value",
    "trend_updates": "skill-defined value",
    "idea_candidates": "skill-defined value",
    "recommended_action": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Scripts, calendar changes, paid tools, and publishing remain approval-gated.

## Memory Rules

- Store full brief in Daily Intelligence and summary in Agent Memory.

## Failure Handling

- If sources are unavailable, produce a partial brief and log coverage gaps.

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
