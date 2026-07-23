# Analytics and Learning Skill

## Purpose

Interpret content and platform performance, generate hypotheses, and recommend measurable next experiments.

## Triggers

- Review analytics
- What worked?
- Why did this perform?
- Monthly review
- Improve content

## Required Context

- Metric snapshots
- Content metadata
- Platform
- Series
- Hook type
- Audience
- Historical baselines

## Tools and Dependencies

- Analytics database
- Charting
- Experiment manager
- Memory

## Workflow

1. Normalize metrics by platform and content type.
2. Compare performance with similar content and baselines.
3. Identify correlations without overstating causation.
4. Generate possible drivers.
5. Create working hypotheses with confidence.
6. Recommend one or more controlled experiments.
7. Promote or reject prior learnings based on evidence.

## Required Outputs

- performance_summary
- insights
- hypotheses
- experiments
- recommended_actions

## Standard Output Envelope

```json
{
  "skill": "20_analytics_review",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "performance_summary": "skill-defined value",
    "insights": "skill-defined value",
    "hypotheses": "skill-defined value",
    "experiments": "skill-defined value",
    "recommended_actions": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Strategy changes based on analytics require review.

## Memory Rules

- Store lessons through Raw Observation → Tested Insight → Approved Learning.

## Failure Handling

- Do not conclude causation from isolated posts.

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
