# Editorial Calendar Orchestration Skill

## Purpose

Build and maintain monthly, weekly, campaign, and platform schedules.

## Triggers

- Plan my week
- Create August calendar
- Schedule content
- Rebalance the calendar
- What should I post?

## Required Context

- Content goals
- Available hours
- Pillars
- Series
- Campaigns
- Pipeline
- Production capacity

## Tools and Dependencies

- Calendar
- Idea scoring
- Pipeline
- Analytics

## Workflow

1. Confirm time period and capacity.
2. Review strategic goals and active campaigns.
3. Select content based on priority and readiness.
4. Balance platforms, pillars, series, and production load.
5. Schedule content and review dates.
6. Identify risks and gaps.
7. Create a minimum viable fallback plan.

## Required Outputs

- editorial_plan
- calendar_events
- capacity_summary
- gaps
- fallback_plan

## Standard Output Envelope

```json
{
  "skill": "19_calendar_orchestration",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "editorial_plan": "skill-defined value",
    "calendar_events": "skill-defined value",
    "capacity_summary": "skill-defined value",
    "gaps": "skill-defined value",
    "fallback_plan": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Founder approves major schedule changes and campaign commitments.

## Memory Rules

- Store planned versus actual execution for future capacity estimates.

## Failure Handling

- Do not overbook beyond stated weekly capacity.

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
