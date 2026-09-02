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


class SeasonIn(_In):
    name: str = Field(min_length=1, max_length=100)
    number: PositiveInt
    roster_size: PositiveInt = 3
    draft_open: bool = True


class ContestantIn(_In):
    name: str = Field(min_length=1, max_length=100)
    tribe: str | None = None
    status: ContestantStatus = ContestantStatus.ACTIVE
    eliminated_episode: PositiveInt | None = None


class EpisodeStatIn(_In):
    events: dict[EventType, NonNegativeInt] = Field(default_factory=dict)


class RosterIn(_In):
    display_name: str = Field(min_length=1, max_length=50)
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


class ContestantPointsOut(BaseModel):
    points: dict[str, int]


class ScoringRulesOut(BaseModel):
    points: dict[EventType, int]
