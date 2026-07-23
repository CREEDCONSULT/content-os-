# Audience Intelligence Skill

## Purpose

Understand audience segments, questions, language, pain points, objections, and desired transformations.

## Triggers

- Who is this for?
- What would my audience think?
- Analyze comments
- Create audience persona
- Find audience pain points

## Required Context

- Audience Persona System
- Published content
- Comments
- DM summaries
- Survey data
- Current offer

## Tools and Dependencies

- Analytics
- Comment ingestion
- Survey import
- Web research
- Vault search

## Workflow

1. Identify the target audience or infer the likely primary segment.
2. Collect relevant behavioural and language evidence.
3. Cluster pains, desires, objections, and recurring questions.
4. Distinguish stated needs from inferred needs.
5. Map findings to content pillars and offers.
6. Create or update persona records.
7. Recommend language and content angles.

## Required Outputs

- persona_updates
- pain_points
- desired_outcomes
- language_patterns
- content_opportunities

## Standard Output Envelope

```json
{
  "skill": "02_audience_intelligence",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "persona_updates": "skill-defined value",
    "pain_points": "skill-defined value",
    "desired_outcomes": "skill-defined value",
    "language_patterns": "skill-defined value",
    "content_opportunities": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Persona redefinition requires review before becoming canonical.

## Memory Rules

- Store audience signals with source, date, confidence, and segment.

## Failure Handling

- Do not generalize from tiny samples without confidence labels.

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
