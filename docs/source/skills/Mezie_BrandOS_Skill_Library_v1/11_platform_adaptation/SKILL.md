# Platform Adaptation Skill

## Purpose

Adapt one core idea into platform-native versions without losing message consistency.

## Triggers

- Adapt for LinkedIn
- Turn this Reel into an X thread
- Repurpose this
- Make platform versions

## Required Context

- Master content item
- Platform playbooks
- Audience behaviour
- Visual identity
- Brand voice

## Tools and Dependencies

- Scriptwriting
- Caption writing
- Carousel builder
- Thread builder

## Workflow

1. Identify the core invariant message.
2. Determine each platform’s native format, length, tone, and CTA.
3. Create separate adaptations rather than copy-pasting.
4. Preserve consistent positioning.
5. Add platform-specific production and publishing notes.
6. Link all derivatives to the master content item.

## Required Outputs

- platform_variants
- publishing_notes
- asset_requirements

## Standard Output Envelope

```json
{
  "skill": "11_platform_adaptation",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "platform_variants": "skill-defined value",
    "publishing_notes": "skill-defined value",
    "asset_requirements": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Final approval required before publication.

## Memory Rules

- Store adaptations and compare later performance by platform.

## Failure Handling

- Do not force content onto a platform where it lacks fit.

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
