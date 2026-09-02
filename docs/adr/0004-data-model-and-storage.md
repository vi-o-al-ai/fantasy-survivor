# 0004. Data model and single-table DynamoDB storage

Date: 2026-09-02
Status: Accepted

## Context

The app needs to store seasons, castaways, per-episode scoring events, and
each player's roster, then compute a leaderboard. Traffic is bursty (air
night) and tiny otherwise. Tests must run without AWS.

## Decision

**Entities** (`backend/app/domain/models.py`): `Season`, `Contestant`,
`EpisodeStat` (event counts for one contestant in one episode), and
`Roster` (one per user per season). Identity comes from the Auth0 `sub`;
there is no user table. Entities are frozen Pydantic models, used both at
the API boundary and for storage serialisation.

**Scoring** (`backend/app/domain/scoring.py`) is pure: points per event
type live in `DEFAULT_POINTS`, `contestant_totals` sums stats, and
`leaderboard` ranks rosters. Per-season rule overrides can be added by
storing a `ScoringRules` on the season later without touching the API.

**Storage** sits behind a `Store` protocol with two implementations:
`MemoryStore` for tests and quick local runs, `DynamoDBStore` for AWS and
DynamoDB Local. One DynamoDB table, keys `PK`/`SK`:

| Item        | PK             | SK                                |
| ----------- | -------------- | --------------------------------- |
| Season      | `SEASONS`      | `SEASON#<id>`                     |
| Contestant  | `SEASON#<sid>` | `CONTESTANT#<id>`                 |
| EpisodeStat | `SEASON#<sid>` | `STAT#EP<episode:03d>#<cid>`      |
| Roster      | `SEASON#<sid>` | `ROSTER#<user_id>`                |

A season is one partition, so every read the app does today is a single
`Query` with a `begins_with` on the sort key. The layout is pinned by a
test; changing it is a data migration.

A contract test suite runs identically against both stores, DynamoDB via
`moto`, so behaviour cannot drift between local and deployed.

## Consequences

- No GSIs yet. "All rosters for a user across seasons" would need one;
  add it when the feature exists.
- A single hot partition per season is fine at fantasy-league scale
  (thousands of items, not millions).
- Numbers are integers only; DynamoDB's `Decimal` handling never comes up.
- Every write is a full-item upsert. Concurrency control (conditional
  writes) is deferred until two admins edit the same episode.
