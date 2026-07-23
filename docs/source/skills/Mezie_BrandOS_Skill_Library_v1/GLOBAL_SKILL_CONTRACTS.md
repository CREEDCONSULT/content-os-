# BRANDOS GLOBAL SKILL CONTRACTS

## Input Envelope

```json
{
  "request_id": "uuid",
  "user_id": "string",
  "brand_id": "string",
  "channel": "dashboard|telegram|heartbeat|api",
  "intent": "string",
  "raw_input": {},
  "context_pack_id": "string|null",
  "permissions": [],
  "budget": {
    "model_usd": 0,
    "tool_usd": 0
  },
  "approval_state": "none|pending|approved|rejected"
}
```

## Output Envelope

```json
{
  "skill": "string",
  "status": "success|partial|blocked|failed",
  "summary": "string",
  "outputs": {},
  "sources": [],
  "memory_writes": [],
  "dashboard_writes": [],
  "approvals_required": [],
  "warnings": [],
  "next_actions": [],
  "confidence": 0.0
}
```

## Non-Negotiable Rules

1. Retrieve relevant context before generation.
2. Prefer canonical records over drafts.
3. Separate facts, approved strategy, hypothesis, and inference.
4. Preserve provenance.
5. Do not fabricate founder experiences, analytics, evidence, or quotes.
6. Do not publish or spend above budget without approval.
7. Do not silently change canonical brand identity.
8. Log meaningful actions.
9. Use the least expensive model capable of the task.
10. Return partial results honestly when tools or evidence are unavailable.
