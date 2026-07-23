# Calendar and Production

Last verified: 2026-07-23

## Connected path

```text
Approved final script
  -> generated production plan
  -> scenes and shot list
  -> location and schedule
  -> critical pre-shoot checklist
  -> server-computed 100% readiness
  -> content advances to ready_to_shoot
```

The transition is enforced in the API. A non-demo content item cannot enter
`ready_to_shoot` through the generic transition endpoint unless it has:

1. an approved final script;
2. a production plan in `ready` state;
3. a readiness score of exactly 100;
4. no active production blockers.

## Capacity-first calendar

Each weekly plan stores available hours, maximum shoots, maximum edits, a fallback
plan, and operator notes. Incoming calendar events are checked against the
capacity plan for their Monday-starting week.

- An event that would exceed available hours returns HTTP `409`.
- A shoot or edit beyond its weekly count returns HTTP `409`.
- The default capacity is 10 hours, 2 shoots, and 3 edits when no explicit plan
  exists.
- Scheduling is internal only. No public platform or external calendar action is
  performed.

## Production readiness

Creating a plan is idempotent per script. The initial phone-first plan contains:

- a creative treatment and technical direction;
- equipment, wardrobe, props, lighting, and music notes;
- three scenes and two shots per scene;
- pre-shoot and post-shoot checklist records;
- an initial blocker list.

Readiness is calculated from durable records:

| Gate | Weight |
|---|---:|
| Approved final script | 20 |
| Scheduled shoot | 15 |
| Confirmed location | 10 |
| Equipment list | 10 |
| Critical pre-shoot checklist | 45 |

Post-shoot checklist items remain important but do not incorrectly block the
pre-shoot readiness calculation.

## API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/calendar/capacity` | List weekly capacity plans |
| `PUT` | `/api/v1/calendar/capacity` | Create or update a normalized week |
| `GET` | `/api/v1/calendar/events` | List scheduled internal work |
| `POST` | `/api/v1/calendar/events` | Add an event after capacity validation |
| `GET` | `/api/v1/production/plans` | List complete production plans |
| `POST` | `/api/v1/production/plans/from-script/{id}` | Build a plan from an approved script |
| `PATCH` | `/api/v1/production/plans/{id}` | Update logistics |
| `POST` | `/api/v1/production/checklist/{id}` | Set checklist completion |

## Seed disclosure

Capacity plans and calendar events across August, October, and December 2026 are
visibly labeled as demo data. The seeded production plan is intentionally blocked
and does not represent completed work.
