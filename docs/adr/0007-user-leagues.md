# 0007. User-created leagues over shared truth

Date: 2026-09-02
Status: Accepted

## Context

Players want to run their own leagues with friends and tweak how points
are awarded, without everyone having to agree on one rule set. Recording
what happened in an episode is tedious and should only be done once.

## Decision

Two layers:

- **Truth** (commissioner-only writes): seasons, contestants, and
  per-episode event counts. Shared by every league for that season.
- **Leagues** (any user): a league belongs to a season, has an owner, a
  join code, roster size, a draft-open flag, and `scoring_overrides`, a
  map of event type to points that is layered over the defaults. Members
  hold their roster on their membership record. Leaderboards apply the
  league's rules to the season's truth at read time; nothing is
  precomputed.

Leagues are private: only members can read them, only the owner sees the
join code or changes settings. Ids are `<slug>-<6 hex>` so links are
readable but not guessable; the join code is the actual gate.

`GET /seasons/{id}/points` remains as the canonical, default-rules view.

## Consequences

- Changing a league's rules re-scores history instantly, which is the
  intended behaviour (rules are a lens, not a ledger).
- Per-league overrides of the *events themselves* are not supported. If
  wanted, they would be a separate `LEAGUE#<id>` / `ADJUST#...` item
  applied after the truth, never a mutation of it.
- "My leagues" is served by a pointer item under `USER#<sub>` rather than
  a GSI, written with every member put. Removing a member must delete
  both items (membership removal is not implemented yet).
