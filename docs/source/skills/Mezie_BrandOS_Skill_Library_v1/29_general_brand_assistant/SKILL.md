# General Brand Assistant Skill

## Purpose

Handle low-risk requests that do not require a specialist workflow while preserving brand context and routing learnings.

## Triggers

- General questions
- Simple summaries
- Low-risk brainstorming
- Status questions

## Required Context

- Brand overview
- Current task context
- User preferences

## Tools and Dependencies

- Vault search
- Database

## Workflow

1. Answer the request directly.
2. Use existing brand context.
3. Avoid creating strategic changes.
4. Offer the correct specialist workflow when needed.
5. Log missing capability patterns.

## Required Outputs

- response
- suggested_next_skill

## Standard Output Envelope

```json
{
  "skill": "29_general_brand_assistant",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "response": "skill-defined value",
    "suggested_next_skill": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- None for low-risk responses.

## Memory Rules

- Save only meaningful decisions or repeated preferences.

## Failure Handling

- Escalate to Skill Router when risk or complexity increases.

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
