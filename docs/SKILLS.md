# Skills

BrandOS imports the supplied 30-skill library into `skill_definitions`. Every
record preserves its slug, contract, risk level, approval policy, source path,
checksum, and enabled state.

## Runtime sequence

1. `00_skill_router` deterministically maps intent and input to candidate skills.
2. Domain skills are selected from explicit keyword routes.
3. `26_context_pack_builder` assembles canonical brand context and eligible memory.
4. `27_agent_transparency` ensures the run ledger exposes inputs, tools, models,
   budgets, writes, approvals, errors, confidence, and next actions.
5. If no domain route matches, `29_general_brand_assistant` handles the request.

The router does not let a model choose its own authority.

## Skill domains

- Strategy and intelligence: `01`–`05`.
- Ideas and authoring: `06`–`12`.
- Production and review: `13`–`15`.
- Safety and workflow: `16`–`19`.
- Learning and evidence: `20`–`23`.
- Capture, memory, and governance: `24`–`29`.

The source contracts remain under
`docs/source/skills/Mezie_BrandOS_Skill_Library_v1`. Runtime definitions are
seeded from those files; they are not handwritten substitutes.

## Governance

- Financial, publishing, canonical, expensive, and other high-risk work creates
  or requires an approval record.
- Budget limits are checked before provider execution.
- Disabled integrations cannot be implied or simulated as live.
- Context packs include provenance and omit restricted or conflicted memory.
- OpenAI structured output uses strict JSON schema through the Responses API,
  with `store: false`; deterministic mock output is the default.
- Approved runs do not auto-resume in this MVP. The operator starts a new,
  auditable run.

Use `GET /api/v1/agent/skills` to inspect the connected definitions and
`GET /api/v1/agent/runs` to audit execution.
