# BrandOS Skill Router

## Purpose

Classify incoming requests, select the correct skill or skill chain, load the minimum relevant context, and enforce approval and safety rules.

## Triggers

- Any dashboard request
- Any Telegram message
- Any scheduled heartbeat event
- Any uploaded link, image, video, audio, or document

## Required Context

- Current user
- Active brand
- Current campaign
- Brand canonical rules
- Permissions
- Budget policy

## Tools and Dependencies

- Database
- Vault search
- Model router
- Approval service
- Agent run logger

## Workflow

1. Normalize the request and identify intent.
2. Classify into one or more skill categories.
3. Resolve ambiguity using existing context before asking the user.
4. Load only the context packs required by the selected skills.
5. Check permissions, brand boundaries, and budget.
6. Create an execution plan.
7. Run skills sequentially or in parallel where safe.
8. Validate outputs against schemas.
9. Write results to the dashboard and memory according to policy.
10. Return a concise user-facing result and next action.

## Required Outputs

- selected_skills
- execution_plan
- context_pack_ids
- approval_requirements
- result_references

## Standard Output Envelope

```json
{
  "skill": "00_skill_router",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "selected_skills": "skill-defined value",
    "execution_plan": "skill-defined value",
    "context_pack_ids": "skill-defined value",
    "approval_requirements": "skill-defined value",
    "result_references": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Required when a downstream skill proposes publishing, paid tool usage above budget, canonical strategy changes, or sensitive founder-story use.

## Memory Rules

- Save routing decisions, execution summaries, failures, and useful intent patterns.

## Failure Handling

- If no skill matches, route to General Brand Assistant and flag the missing capability for future skill development.

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
