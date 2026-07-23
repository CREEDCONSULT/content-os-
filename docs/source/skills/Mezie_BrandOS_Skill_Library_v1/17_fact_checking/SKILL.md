# Research and Fact-Checking Skill

## Purpose

Verify claims, dates, statistics, quotations, platform changes, and current events before publication.

## Triggers

- Verify this
- Fact-check script
- Add evidence
- Is this current?
- Research this topic

## Required Context

- Draft content
- Required freshness
- Approved source hierarchy
- Citation rules

## Tools and Dependencies

- Web search
- Primary-source retrieval
- Document search
- Source logger

## Workflow

1. Extract factual claims.
2. Classify each claim by freshness and risk.
3. Find authoritative sources.
4. Resolve conflicts or state disagreement.
5. Record source, date, and confidence.
6. Recommend corrections.
7. Return verified copy.

## Required Outputs

- claim_table
- verified_text
- sources
- confidence
- unresolved_claims

## Standard Output Envelope

```json
{
  "skill": "17_fact_checking",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "claim_table": "skill-defined value",
    "verified_text": "skill-defined value",
    "sources": "skill-defined value",
    "confidence": "skill-defined value",
    "unresolved_claims": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- No special approval, but unresolved high-risk claims block publication.

## Memory Rules

- Save reusable research notes and source records.

## Failure Handling

- Never invent citations or imply verification when sources are insufficient.

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
