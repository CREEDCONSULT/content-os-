# Brand Asset Management Skill

## Purpose

Ingest, classify, tag, retrieve, and connect visual, audio, video, and document assets.

## Triggers

- Upload asset
- Find B-roll
- Attach this footage
- Organize photos
- Find my logo

## Required Context

- Asset taxonomy
- Content items
- Projects
- Usage rights
- Visual identity

## Tools and Dependencies

- Object storage
- Metadata extraction
- Vision tagging
- Search

## Workflow

1. Ingest the asset and preserve original file.
2. Extract metadata.
3. Generate tags and preview.
4. Record rights, people, location, project, orientation, and quality.
5. Link to relevant content items.
6. Flag duplicates or restricted use.

## Required Outputs

- asset_record
- tags
- preview
- linked_content

## Standard Output Envelope

```json
{
  "skill": "23_asset_management",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "asset_record": "skill-defined value",
    "tags": "skill-defined value",
    "preview": "skill-defined value",
    "linked_content": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Restricted or third-party assets require rights confirmation.

## Memory Rules

- Store metadata and usage history, not unnecessary duplicate embeddings.

## Failure Handling

- Never assume usage rights.

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
