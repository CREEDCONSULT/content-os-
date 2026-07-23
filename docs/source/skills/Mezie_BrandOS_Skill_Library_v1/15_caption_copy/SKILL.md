# Caption and Social Copy Skill

## Purpose

Create captions, post copy, CTAs, titles, descriptions, and supporting text for each platform.

## Triggers

- Write caption
- Create title
- Write YouTube description
- Create CTA
- Write carousel copy

## Required Context

- Content item
- Platform
- Audience
- Brand voice
- Campaign
- SEO or discovery needs

## Tools and Dependencies

- Platform Adaptation
- Keyword research
- Hashtag guidance

## Workflow

1. Identify the role of the copy.
2. Create a strong first line.
3. Support the content without repeating the entire script.
4. Add context, value, and platform-native CTA.
5. Use discoverability elements where relevant.
6. Check tone and claims.

## Required Outputs

- caption
- title_options
- description
- cta_options
- keywords

## Standard Output Envelope

```json
{
  "skill": "15_caption_copy",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "caption": "skill-defined value",
    "title_options": "skill-defined value",
    "description": "skill-defined value",
    "cta_options": "skill-defined value",
    "keywords": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Final publication approval required.

## Memory Rules

- Track copy patterns and performance.

## Failure Handling

- Avoid spammy hashtags, false urgency, and generic filler.

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
