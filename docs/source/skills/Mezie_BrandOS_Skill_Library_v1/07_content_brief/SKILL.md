# Content Brief Skill

## Purpose

Convert an approved idea into a precise, platform-ready content brief before scripting.

## Triggers

- Create brief
- Develop this idea
- Prepare this for Instagram
- Turn this into a campaign asset

## Required Context

- Idea record
- Audience
- Platform playbook
- Series template
- Brand voice
- Relevant proof
- Benchmark references

## Tools and Dependencies

- Vault search
- Creator Intelligence
- Research
- Evidence checker

## Workflow

1. Define objective, audience, platform, format, pillar, and series.
2. Clarify the core message and audience problem.
3. Select desired emotion and action.
4. Retrieve relevant founder stories, proof, and benchmarks.
5. Define visual direction and production constraints.
6. Set duration, CTA, and success metric.
7. Check boundaries and evidence.
8. Generate the structured brief.

## Required Outputs

- content_brief

## Standard Output Envelope

```json
{
  "skill": "07_content_brief",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "content_brief": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- High-value campaigns or sensitive stories should be approved before scripting.

## Memory Rules

- Save brief linked to source idea, campaign, and future script.

## Failure Handling

- If proof is missing, mark the brief as Proof Needed and create a research task.

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
