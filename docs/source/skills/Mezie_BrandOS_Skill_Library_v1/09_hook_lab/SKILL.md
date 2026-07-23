# Hook Lab Skill

## Purpose

Generate, classify, score, test, and preserve high-performing hooks.

## Triggers

- Improve hook
- Give me 10 hooks
- Why is this opening weak?
- Test hooks
- Find my best hook

## Required Context

- Topic
- Audience
- Platform
- Brand voice
- Hook library
- Historical performance
- Benchmark patterns

## Tools and Dependencies

- Analytics
- Creator Intelligence
- A/B experiment manager

## Workflow

1. Identify the desired psychological effect.
2. Generate hooks across several categories.
3. Score clarity, curiosity, specificity, brand fit, audience fit, and originality.
4. Compare with prior winning and overused hooks.
5. Recommend top options and explain use cases.
6. Create a test plan when appropriate.

## Required Outputs

- hook_options
- scores
- recommended_hook
- test_plan

## Standard Output Envelope

```json
{
  "skill": "09_hook_lab",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "hook_options": "skill-defined value",
    "scores": "skill-defined value",
    "recommended_hook": "skill-defined value",
    "test_plan": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- No approval for generation; script approval covers final selection.

## Memory Rules

- Store winning hooks, rejected hooks, test results, and fatigue warnings.

## Failure Handling

- Avoid manipulative clickbait unsupported by the content.

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
