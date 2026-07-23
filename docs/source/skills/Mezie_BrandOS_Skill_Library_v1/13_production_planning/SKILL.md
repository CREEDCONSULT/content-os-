# Production Planning Skill

## Purpose

Turn an approved script and creative direction into an executable shoot plan.

## Triggers

- Prepare shoot
- Create shot list
- What do I need tomorrow?
- Production checklist
- Ready this video

## Required Context

- Approved script
- Creative treatment
- Equipment inventory
- Location
- Schedule
- Asset library

## Tools and Dependencies

- Calendar
- Checklist engine
- Shot planner
- Asset manager

## Workflow

1. Break the script into scenes and shots.
2. Assign framing, movement, dialogue, B-roll, and duration.
3. Create equipment, wardrobe, prop, and location lists.
4. Generate pre-shoot and post-shoot checklists.
5. Estimate readiness and identify blockers.
6. Schedule the production task.

## Required Outputs

- production_plan
- shot_list
- checklists
- readiness_score
- blockers

## Standard Output Envelope

```json
{
  "skill": "13_production_planning",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "production_plan": "skill-defined value",
    "shot_list": "skill-defined value",
    "checklists": "skill-defined value",
    "readiness_score": "skill-defined value",
    "blockers": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Shoot scheduling or external costs require approval.

## Memory Rules

- Store production outcomes, missing shots, and reusable setup templates.

## Failure Handling

- Do not mark Ready to Shoot while critical blockers remain.

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
