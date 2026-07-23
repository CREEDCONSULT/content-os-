# Platform Scriptwriting Skill

## Purpose

Write original, brand-aligned scripts tailored to platform, format, audience, and production reality.

## Triggers

- Write script
- Draft Reel
- Create YouTube script
- Turn this brief into a video
- Rewrite this script

## Required Context

- Approved brief
- Brand voice
- Platform playbook
- Series format
- Founder stories
- Evidence
- Production constraints

## Tools and Dependencies

- Vault search
- Hook Lab
- Fact checker
- Platform Adaptation
- Version manager

## Workflow

1. Confirm platform, duration, audience, and objective.
2. Generate multiple hook options.
3. Choose the strongest structure for the content type.
4. Write spoken lines, on-screen text, B-roll, camera, and CTA.
5. Preserve founder voice and avoid copied language.
6. Estimate duration.
7. Check brand fit, clarity, originality, evidence, and risk.
8. Create versioned draft.

## Required Outputs

- script
- hook_variants
- duration_estimate
- visual_notes
- brand_alignment_score

## Standard Output Envelope

```json
{
  "skill": "08_scriptwriting",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "script": "skill-defined value",
    "hook_variants": "skill-defined value",
    "duration_estimate": "skill-defined value",
    "visual_notes": "skill-defined value",
    "brand_alignment_score": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Final script approval required before Ready to Shoot.

## Memory Rules

- Store every version, revision reason, and final approved version.

## Failure Handling

- Do not fabricate personal stories, results, quotes, or facts.

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
