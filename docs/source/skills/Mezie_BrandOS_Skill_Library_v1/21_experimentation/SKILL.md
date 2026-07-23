# Content Experimentation Skill

## Purpose

Design, track, and evaluate controlled content experiments.

## Triggers

- Test this hook
- Run an experiment
- Compare formats
- A/B test
- Validate this hypothesis

## Required Context

- Hypothesis
- Historical metrics
- Content constraints
- Platform
- Available sample size

## Tools and Dependencies

- Calendar
- Analytics
- Content Pipeline

## Workflow

1. Define the question and hypothesis.
2. Choose one primary variable.
3. Define control conditions.
4. Set success metric and measurement window.
5. Schedule the test.
6. Collect results.
7. Evaluate confidence and practical significance.
8. Record decision.

## Required Outputs

- experiment_plan
- scheduled_items
- result_summary
- decision

## Standard Output Envelope

```json
{
  "skill": "21_experimentation",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "experiment_plan": "skill-defined value",
    "scheduled_items": "skill-defined value",
    "result_summary": "skill-defined value",
    "decision": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Founder approves tests that materially alter public positioning or spend.

## Memory Rules

- Store all experiments, including failed tests.

## Failure Handling

- Reject experiments with too many uncontrolled variables.

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
