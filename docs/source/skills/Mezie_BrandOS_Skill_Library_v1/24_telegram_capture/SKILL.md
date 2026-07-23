# Telegram Capture and Command Skill

## Purpose

Convert Telegram text, links, images, files, and voice notes into structured BrandOS records and workflows.

## Triggers

- /idea
- /research
- /benchmark
- /script
- /review
- /plan
- /shoot
- /status
- /today
- /week
- /approve
- Natural-language Telegram requests

## Required Context

- Telegram user identity
- Current brand
- Recent conversation
- Permissions
- Active campaign

## Tools and Dependencies

- Telegram Bot API
- Transcription
- Skill Router
- Dashboard API

## Workflow

1. Authenticate the sender.
2. Classify the message.
3. Download and preserve attachments where allowed.
4. Transcribe voice notes.
5. Route to the correct skill.
6. Create or update dashboard records.
7. Return a concise response with dashboard link and approval actions.

## Required Outputs

- telegram_response
- created_records
- dashboard_links
- approval_buttons

## Standard Output Envelope

```json
{
  "skill": "24_telegram_capture",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "telegram_response": "skill-defined value",
    "created_records": "skill-defined value",
    "dashboard_links": "skill-defined value",
    "approval_buttons": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Inline approval buttons may approve only actions within the user’s permission level.

## Memory Rules

- Save meaningful conversation summaries and source message references.

## Failure Handling

- If intent is unclear, return the most likely interpretation and one concise clarification option.

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
