# Content Pipeline Management Skill

## Purpose

Move content through the lifecycle while maintaining ownership, deadlines, blockers, and approvals.

## Triggers

- Update status
- What is blocked?
- Move this to production
- Show pipeline
- Plan my week

## Required Context

- Content records
- Calendar
- Tasks
- Approvals
- Production status

## Tools and Dependencies

- Database
- Calendar
- Task manager
- Notification service

## Workflow

1. Identify the relevant content item.
2. Validate prerequisites for the requested status.
3. Update status and timestamps.
4. Create or close dependent tasks.
5. Notify required reviewers.
6. Surface blockers and overdue items.
7. Record the change.

## Required Outputs

- updated_content_status
- tasks
- notifications
- blockers

## Standard Output Envelope

```json
{
  "skill": "18_content_pipeline",
  "status": "success|partial|blocked",
  "summary": "string",
  "outputs": {
    "updated_content_status": "skill-defined value",
    "tasks": "skill-defined value",
    "notifications": "skill-defined value",
    "blockers": "skill-defined value"
  },
  "sources": [],
  "memory_writes": [],
  "approvals_required": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Approval Rules

- Automatic movement into Published is prohibited without approval.

## Memory Rules

- Keep full status history and transition reasons.

## Failure Handling

- Reject invalid transitions and explain missing prerequisites.

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
