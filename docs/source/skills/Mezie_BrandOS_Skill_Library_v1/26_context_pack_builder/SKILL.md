# Context Pack Builder Skill

## Purpose

Assemble concise task-specific context from the full BrandOS memory without overloading model prompts.

## Triggers

- Before most generative or analytical skill runs

## Required Context

- Task intent
- Brand documents
- Relevant memory
- Token budget
- Freshness requirements

## Tools and Dependencies

- Semantic retrieval
- Keyword search
- Context ranking
- Summarization

## Workflow

1. Identify required context categories.
2. Retrieve candidate records.
3. Rank by relevance, authority, freshness, and sensitivity.
4. Prefer canonical records over drafts.
5. Summarize only when needed.
6. Include provenance and exclusions.
7. Return the smallest sufficient context pack.

## Required Outputs

- context_pack
- source_records
- token_estimate
- freshness_notes

## Standard Output Envelope

```json
{
  "skill": "26_context_pack_builder",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "context_pack": "skill-defined value",
    "source_records": "skill-defined value",
    "token_estimate": "skill-defined value",
    "freshness_notes": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- No approval for retrieval; sensitive records follow access rules.

## Memory Rules

- Track which context packs produce useful outcomes.

## Failure Handling

- If critical context is missing, stop and request or create a research task.

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
