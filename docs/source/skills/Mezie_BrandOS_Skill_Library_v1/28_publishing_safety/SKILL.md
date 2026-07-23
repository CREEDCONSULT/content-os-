# Publishing and Approval Safety Skill

## Purpose

Control final publishing actions and enforce platform, legal, brand, and permission checks.

## Triggers

- Publish
- Schedule post
- Send live
- Approve final
- Distribute content

## Required Context

- Approved content
- Platform account
- Final assets
- Brand boundaries
- Fact-check status
- Permissions

## Tools and Dependencies

- Platform APIs
- Scheduler
- Approval service
- Audit log

## Workflow

1. Verify final content version.
2. Confirm all required approvals.
3. Confirm platform formatting.
4. Check rights, facts, claims, links, and disclosures.
5. Generate final preview.
6. Schedule or publish only after explicit approval.
7. Record publication URL and timestamp.

## Required Outputs

- publication_record
- platform_result
- audit_log

## Standard Output Envelope

```json
{
  "skill": "28_publishing_safety",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "publication_record": "skill-defined value",
    "platform_result": "skill-defined value",
    "audit_log": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Explicit human approval is mandatory for MVP and initial production phases.

## Memory Rules

- Store final content, publication metadata, and downstream analytics linkage.

## Failure Handling

- Abort on missing approval, failed fact check, missing rights, or platform mismatch.

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
