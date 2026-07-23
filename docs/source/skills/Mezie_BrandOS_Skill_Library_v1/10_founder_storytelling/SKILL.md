# Founder Storytelling Skill

## Purpose

Retrieve, structure, and safely adapt founder experiences into public stories.

## Triggers

- Tell my story
- Use my food business story
- Create founder narrative
- Write a personal post
- Can I talk about this?

## Required Context

- Founder Story Library
- Story safety levels
- Brand voice
- Audience
- Public boundaries
- Evidence

## Tools and Dependencies

- Vault retrieval
- Privacy checker
- Narrative builder

## Workflow

1. Retrieve the relevant founder story.
2. Check safety classification and privacy restrictions.
3. Identify theme, tension, decision, outcome, and lesson.
4. Choose a platform-appropriate structure.
5. Protect third-party identities and sensitive details.
6. Connect the lesson to the audience.
7. Generate script or post draft.

## Required Outputs

- story_structure
- draft
- privacy_notes
- safety_level

## Standard Output Envelope

```json
{
  "skill": "10_founder_storytelling",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "story_structure": "skill-defined value",
    "draft": "skill-defined value",
    "privacy_notes": "skill-defined value",
    "safety_level": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Yellow and Red stories require explicit founder approval.

## Memory Rules

- Save approved public versions separately from private source notes.

## Failure Handling

- Do not infer or embellish missing personal details.

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
