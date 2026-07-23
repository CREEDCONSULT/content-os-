# Brand Memory and Vault Skill

## Purpose

Write, retrieve, promote, archive, and govern BrandOS knowledge across the dedicated Obsidian vault and database.

## Triggers

- Remember this
- Find prior decision
- Update the vault
- What did we decide?
- Save this insight

## Required Context

- Vault governance
- Memory types
- Canonical rules
- Access permissions
- Record provenance

## Tools and Dependencies

- Obsidian vault
- PostgreSQL
- pgvector or Qdrant
- Creed Memory sync

## Workflow

1. Classify the information by memory type.
2. Check sensitivity and approval requirements.
3. Create or update the correct note and database record.
4. Add provenance, date, confidence, tags, links, and review date.
5. Index for retrieval.
6. Sync only approved summaries to general Creed Memory.
7. Archive superseded records rather than deleting silently.

## Required Outputs

- memory_record
- vault_path
- links
- sync_status

## Standard Output Envelope

```json
{
  "skill": "25_brand_memory",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "memory_record": "skill-defined value",
    "vault_path": "skill-defined value",
    "links": "skill-defined value",
    "sync_status": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Canonical and sensitive memory writes require approval.

## Memory Rules

- This skill governs memory itself.

## Failure Handling

- Prevent duplicate canonical notes and conflicting active versions.

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
