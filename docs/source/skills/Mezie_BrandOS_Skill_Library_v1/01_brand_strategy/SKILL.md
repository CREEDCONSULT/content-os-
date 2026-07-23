# Brand Strategy Skill

## Purpose

Evaluate and develop positioning, category ownership, audience focus, brand promise, differentiation, campaign strategy, and strategic coherence.

## Triggers

- Review my positioning
- Is this on brand?
- Develop a campaign
- Who is this for?
- Should I pursue this opportunity?

## Required Context

- Founder Identity OS
- Positioning Architecture
- Audience Personas
- Brand Boundaries
- Current campaigns
- Proof-of-work roadmap

## Tools and Dependencies

- Vault search
- Database
- Web research when freshness is required
- Comparison engine

## Workflow

1. Identify the strategic decision being made.
2. Retrieve relevant canonical brand documents.
3. Separate current fact, approved strategy, working hypothesis, and model inference.
4. Assess audience fit, brand fit, market relevance, proof availability, and risk.
5. Generate options with trade-offs.
6. Recommend one direction and explain why.
7. Define measurable success criteria.
8. Record the decision and review date.

## Required Outputs

- strategic_assessment
- recommended_direction
- alternatives
- risks
- success_metrics
- decision_record

## Standard Output Envelope

```json
{
  "skill": "01_brand_strategy",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "strategic_assessment": "skill-defined value",
    "recommended_direction": "skill-defined value",
    "alternatives": "skill-defined value",
    "risks": "skill-defined value",
    "success_metrics": "skill-defined value",
    "decision_record": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Canonical positioning, audience, values, or boundary changes require founder approval.

## Memory Rules

- Approved decisions go to Canonical Decisions; unapproved ideas remain Working Hypotheses.

## Failure Handling

- When evidence is weak, label the recommendation provisional and specify what evidence is missing.

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
