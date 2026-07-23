# Content Ideation Skill

## Purpose

Turn raw thoughts, audience questions, trends, stories, and projects into scored content ideas.

## Triggers

- Give me ideas
- Turn this into content
- Capture this idea
- What can I post about this?
- Generate a series

## Required Context

- Content pillars
- Series
- Audience
- Current calendar
- Recent ideas
- Published content
- Trend data

## Tools and Dependencies

- Vault search
- Idea scoring
- Deduplication
- Trend Research
- Founder Story retrieval

## Workflow

1. Capture the raw input without losing original wording.
2. Identify audience, pillar, series, and platform possibilities.
3. Generate multiple distinct angles.
4. Check for duplication and content fatigue.
5. Score brand fit, audience value, proof, timeliness, originality, feasibility, and strategic importance.
6. Recommend next action: research, brief, script, schedule, watch, or archive.
7. Save the idea.

## Required Outputs

- idea_records
- scores
- recommended_formats
- next_actions

## Standard Output Envelope

```json
{
  "skill": "06_content_ideation",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "idea_records": "skill-defined value",
    "scores": "skill-defined value",
    "recommended_formats": "skill-defined value",
    "next_actions": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- None for idea creation; approval needed to schedule or move into production automatically.

## Memory Rules

- Save source, raw input, derivative ideas, decision, and rejection reason.

## Failure Handling

- If the idea is too broad, produce clarifying assumptions instead of generic content.

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
