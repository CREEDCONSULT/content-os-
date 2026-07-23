# Creator Intelligence Skill

## Purpose

Analyze benchmark creators and content while extracting transferable mechanics without copying identity, wording, or protected expression.

## Triggers

- Analyze this creator
- Benchmark this Reel
- Study this video
- What can I learn from this creator?
- Adapt this style

## Required Context

- Creator watchlist
- Brand voice
- Visual identity
- Audience
- Existing benchmark dossiers
- Copyright policy

## Tools and Dependencies

- Apify
- Web fetch
- Transcription
- Video metadata
- Image analysis
- Vault

## Workflow

1. Detect platform and source type.
2. Acquire permitted evidence.
3. Preserve raw source metadata and provenance.
4. Transcribe and segment the content.
5. Analyze hook, structure, pacing, language, visuals, camera, lighting, editing, CTA, and audience response.
6. Separate transferable mechanics from creator-specific identity.
7. Compare findings with existing patterns.
8. Generate original Mezie adaptations.
9. Save dossier and teardown.

## Required Outputs

- creator_dossier
- content_teardown
- pattern_tags
- transferable_mechanics
- mezie_adaptations
- limitations

## Standard Output Envelope

```json
{
  "skill": "03_creator_intelligence",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "creator_dossier": "skill-defined value",
    "content_teardown": "skill-defined value",
    "pattern_tags": "skill-defined value",
    "transferable_mechanics": "skill-defined value",
    "mezie_adaptations": "skill-defined value",
    "limitations": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Paid acquisition above budget or restricted source access requires approval.

## Memory Rules

- Store evidence, transcript, findings, and adaptation links in Creator Intelligence memory.

## Failure Handling

- If media cannot be acquired, analyze only visible metadata and clearly state limitations.

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
