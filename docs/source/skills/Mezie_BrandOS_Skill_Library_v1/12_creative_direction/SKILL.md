# Creative Direction Skill

## Purpose

Translate a content concept into a coherent visual, sonic, emotional, and cinematic direction.

## Triggers

- Direct this video
- How should this look?
- Create scenes
- Lighting and camera plan
- Improve visual style

## Required Context

- Script
- Visual identity
- Series style
- Location
- Equipment
- Wardrobe
- Benchmark references

## Tools and Dependencies

- Image analysis
- Video analysis
- Shot planner
- Asset library

## Workflow

1. Identify the emotional and strategic purpose.
2. Define visual concept, environment, colour, wardrobe, props, and music direction.
3. Create scene sequence.
4. Specify framing, camera angle, movement, lighting, and B-roll.
5. Ensure production feasibility.
6. Check visual consistency with the BrandOS design language.

## Required Outputs

- creative_treatment
- scene_plan
- visual_references
- lighting_plan
- wardrobe_plan
- music_direction

## Standard Output Envelope

```json
{
  "skill": "12_creative_direction",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "creative_treatment": "skill-defined value",
    "scene_plan": "skill-defined value",
    "visual_references": "skill-defined value",
    "lighting_plan": "skill-defined value",
    "wardrobe_plan": "skill-defined value",
    "music_direction": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Founder approves high-cost or identity-sensitive visual directions.

## Memory Rules

- Save reusable visual patterns and series-specific style rules.

## Failure Handling

- If equipment constraints exist, provide a phone-first alternative.

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
