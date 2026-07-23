# Visual Review Skill

## Purpose

Critique footage, thumbnails, lighting, wardrobe, backgrounds, graphics, and edited videos against brand and platform standards.

## Triggers

- Review this image
- Check lighting
- Review my thumbnail
- Critique this edit
- Is this on brand?

## Required Context

- Visual identity
- Platform requirements
- Creative treatment
- Approved script
- Benchmark references

## Tools and Dependencies

- Vision model
- Video frame extraction
- Audio analysis
- Asset library

## Workflow

1. Identify the asset type and intended use.
2. Assess composition, clarity, lighting, colour, wardrobe, background, text, pacing, and platform fit.
3. Compare with approved direction.
4. Classify issues as Required, Recommended, or Optional.
5. Generate concrete revision instructions.
6. Save review and link to asset.

## Required Outputs

- review_score
- required_changes
- recommended_changes
- optional_experiments

## Standard Output Envelope

```json
{
  "skill": "14_visual_review",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "review_score": "skill-defined value",
    "required_changes": "skill-defined value",
    "recommended_changes": "skill-defined value",
    "optional_experiments": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Final edit approval remains human.

## Memory Rules

- Store recurring visual issues and improvement trends.

## Failure Handling

- State when quality cannot be judged from the available resolution or sample.

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
