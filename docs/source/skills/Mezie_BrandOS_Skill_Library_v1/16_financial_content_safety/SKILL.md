# Financial Content Safety Skill

## Purpose

Ensure market, crypto, stock, ETF, and wealth content remains educational, evidence-based, and within approved boundaries.

## Triggers

- Any financial content
- Market analysis
- Crypto explainer
- Stock discussion
- Gold or macro hypothesis

## Required Context

- Financial Content Boundary
- Evidence
- Current regulations where relevant
- Audience
- Risk language

## Tools and Dependencies

- Web research
- Source verification
- Claim checker

## Workflow

1. Classify the content as education, analysis, opinion, or prohibited signal.
2. Verify current facts and sources.
3. Separate evidence from hypothesis.
4. Identify risks and alternative outcomes.
5. Remove command language and certainty claims.
6. Add appropriate educational framing.
7. Flag regulated or high-risk content.

## Required Outputs

- safety_review
- approved_language
- risk_disclosures
- blocked_claims

## Standard Output Envelope

```json
{
  "skill": "16_financial_content_safety",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "safety_review": "skill-defined value",
    "approved_language": "skill-defined value",
    "risk_disclosures": "skill-defined value",
    "blocked_claims": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- All high-risk financial content requires founder approval.

## Memory Rules

- Store reviewed claims and precedent decisions.

## Failure Handling

- Block guaranteed returns, direct signals, and unsupported performance claims.

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
