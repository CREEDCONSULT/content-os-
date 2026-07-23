# Content Authoring Workflow

Last verified: 2026-07-23

## Connected path

The Script Studio implements the following durable flow:

```text
Idea
  -> structured content brief
  -> immutable script version
  -> scored hook options
  -> manual fact and financial-safety review
  -> pending backend approval
  -> approved script and content item
  -> blocker-free production plan at 100%
  -> ready to shoot
```

The dashboard never advances a non-demo content item into production without an
approved final script.

## Content briefs

Creating a brief links the source idea, operational content item, and brand. The
brief records:

- objective, audience, platform, format, pillar, and series;
- core message and audience problem;
- desired emotion and action;
- proof points and benchmark references;
- visual direction and production constraints;
- duration, CTA, success metric, and evidence state.

Rejected and archived ideas cannot become briefs. Creating a brief never deletes
or overwrites the source idea.

## Script versions

Every script revision creates a new immutable version with:

- selected hook and full body;
- on-screen text, B-roll, and camera notes;
- CTA and duration;
- brand-alignment and originality scores;
- evidence notes, change summary, checksum, author, and timestamp.

The previous version remains available and inactive. A new revision resets the
fact-check and approval states.

## Hook Lab

The current Hook Lab stores each option independently. It records category,
clarity, curiosity, specificity, brand fit, audience fit, originality, total
score, recommendation state, and fatigue warning. Scoring is deterministic for
the local MVP and does not claim predictive performance.

## Fact and financial review

The review record stores claim rows, source references, unresolved claims,
reviewed text, reviewer, confidence, risk disclosures, and blocked claims.

- Any unresolved claim blocks final approval.
- A declared claim without a source blocks final approval.
- Direct buy/sell signals, guaranteed returns, risk-free returns, and similar
  prohibited language are blocked automatically.
- Educational financial content receives risk disclosures and a medium-risk
  classification.
- The interface labels the check as a manual assertion; it does not claim that an
  external research service was called.

## Approval behavior

Submitting a verified script creates a pending `script_final_approval` record.
Approval:

- marks the exact current version as approved;
- updates the script and linked content approval states;
- writes a pipeline event;
- advances the linked content item from `review` to `approved`.

Rejection returns the linked content item to `script` for revision. A real,
non-demo item cannot enter `approved` without final script approval, and cannot
enter `ready_to_shoot` until a production plan has no blockers and reaches 100%
readiness.

Public publishing remains separately gated and is not implemented as an external
platform action.

## API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/studio/briefs` | List content briefs |
| `POST` | `/api/v1/studio/briefs/from-idea/{id}` | Create a linked brief |
| `POST` | `/api/v1/studio/briefs/{id}/scripts` | Create the first script version |
| `GET` | `/api/v1/studio/scripts` | List scripts with current version and review |
| `POST` | `/api/v1/studio/scripts/{id}/versions` | Create an immutable revision |
| `POST` | `/api/v1/studio/scripts/{id}/fact-check` | Record fact and safety review |
| `POST` | `/api/v1/studio/scripts/{id}/submit` | Create final approval |

## Current limitations

- Fact checking is a structured manual workflow; authoritative web research is
  not automated.
- Hook scores are heuristic, not trained performance predictions.
- Rich-text block editing and collaborative comments are deferred.
- Production is connected after approval; external calendar and platform sync are
  deferred.
