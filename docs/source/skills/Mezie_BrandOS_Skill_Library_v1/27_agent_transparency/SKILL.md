# Agent Transparency and Run Logging Skill

## Purpose

Make every important agent action explainable, reviewable, and auditable.

## Triggers

- Every tool-using or multi-step agent run

## Required Context

- Execution plan
- Models
- Tools
- Costs
- Approvals
- Outputs

## Tools and Dependencies

- Run logger
- Cost tracker
- Approval service

## Workflow

1. Create run record before execution.
2. Log selected skills and context.
3. Record tool calls, model aliases, costs, errors, and confidence.
4. Record proposed and completed writes.
5. Surface approvals.
6. Create human-readable run summary.

## Required Outputs

- agent_run_record
- cost_summary
- action_summary
- errors
- approval_log

## Standard Output Envelope

```json
{
  "skill": "27_agent_transparency",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "agent_run_record": "skill-defined value",
    "cost_summary": "skill-defined value",
    "action_summary": "skill-defined value",
    "errors": "skill-defined value",
    "approval_log": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- This skill records approvals but does not grant them.

## Memory Rules

- Store summaries in Agent Run Summaries; detailed logs may remain in database.

## Failure Handling

- A run that cannot be logged should not perform high-risk writes.

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
