# Proof-of-Work and Case Study Skill

## Purpose

Identify, structure, document, and publish evidence that strengthens authority.

## Triggers

- Create case study
- What proof do I have?
- Document this project
- Build credibility
- Prepare portfolio

## Required Context

- Project records
- Outputs
- Results
- Screenshots
- Testimonials
- Authority gaps

## Tools and Dependencies

- Vault
- Asset library
- Analytics
- Client evidence

## Workflow

1. Identify the credibility gap being addressed.
2. Collect project context, constraints, process, output, result, and lessons.
3. Verify claims and permissions.
4. Build the case-study narrative.
5. Select supporting visuals.
6. Create platform and website versions.
7. Update authority ladder.

## Required Outputs

- case_study
- proof_item
- asset_list
- credibility_update

## Standard Output Envelope

```json
{
  "skill": "22_proof_of_work",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "case_study": "skill-defined value",
    "proof_item": "skill-defined value",
    "asset_list": "skill-defined value",
    "credibility_update": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Client-sensitive proof and testimonials require permission.

## Memory Rules

- Store approved case studies and unresolved evidence gaps.

## Failure Handling

- Do not invent outcomes or overstate unfinished work.

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
