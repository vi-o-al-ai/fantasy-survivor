"""Request and response shapes for the HTTP API.

Entities from ``app.domain.models`` are returned directly where they are
already the right shape. Inputs are separate so clients cannot set fields
the path or the token already determine (ids, season, user).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt, field_validator

from app.domain.models import ContestantStatus, EventType, Slug


class _In(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- truth ------------------------------------------------------------------


class SeasonIn(_In):
    name: str = Field(min_length=1, max_length=100)
    number: PositiveInt


class ContestantIn(_In):
    name: str = Field(min_length=1, max_length=100)
    tribe: str | None = None
    status: ContestantStatus = ContestantStatus.ACTIVE
    eliminated_episode: PositiveInt | None = None


class EpisodeStatIn(_In):
    events: dict[EventType, NonNegativeInt] = Field(default_factory=dict)


class ContestantPointsOut(BaseModel):
    points: dict[str, int]


class ScoringRulesOut(BaseModel):
    points: dict[EventType, int]


# --- leagues ----------------------------------------------------------------


class LeagueCreateIn(_In):
    season_id: Slug
    name: str = Field(min_length=1, max_length=60)
    display_name: str = Field(min_length=1, max_length=50, description="Owner's name in the league")
    roster_size: PositiveInt = 3
    scoring_overrides: dict[EventType, int] = Field(default_factory=dict)


class LeagueUpdateIn(_In):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    roster_size: PositiveInt | None = None
    draft_open: bool | None = None
    scoring_overrides: dict[EventType, int] | None = None


class LeagueOut(BaseModel):
    """A league as members see it. The join code is only shown to the owner."""

    id: str
    season_id: str
    name: str
    owner_id: str
    roster_size: int
    draft_open: bool
    scoring_overrides: dict[EventType, int]
    join_code: str | None = None
    is_owner: bool


class JoinLeagueIn(_In):
    join_code: str = Field(min_length=1, max_length=16)
    display_name: str = Field(min_length=1, max_length=50)


class RosterIn(_In):
    contestant_ids: list[Slug]

    @field_validator("contestant_ids")
    @classmethod
    def _unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("contestant_ids must be unique")
        return value


class LeaderboardEntryOut(BaseModel):
    rank: PositiveInt
    user_id: str
    display_name: str
    points: int
    contestant_points: dict[str, int]
