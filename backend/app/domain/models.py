"""Core entities.

Pydantic models are used for entities because the same shape crosses the API
boundary and gets serialised to storage; validation in one place beats three
parallel class hierarchies while the domain is this small.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt, field_validator

# Identifiers are URL-safe slugs chosen by an admin (e.g. "s49", "boston-rob").
Slug = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")]


class EventType(StrEnum):
    """Things that happen to a castaway in an episode and earn (or cost) points."""

    SURVIVED_EPISODE = "survived_episode"
    INDIVIDUAL_IMMUNITY = "individual_immunity"
    TEAM_IMMUNITY = "team_immunity"
    INDIVIDUAL_REWARD = "individual_reward"
    TEAM_REWARD = "team_reward"
    IDOL_FOUND = "idol_found"
    IDOL_PLAYED_SUCCESSFULLY = "idol_played_successfully"
    ADVANTAGE_FOUND = "advantage_found"
    CORRECT_VOTE = "correct_vote"  # voted for the person who went home
    VOTE_RECEIVED = "vote_received"
    FIRE_MAKING_WIN = "fire_making_win"
    VOTED_OUT = "voted_out"
    QUIT_OR_MEDEVAC = "quit_or_medevac"
    FINAL_THREE = "final_three"
    JURY_VOTE_RECEIVED = "jury_vote_received"
    SOLE_SURVIVOR = "sole_survivor"


class ContestantStatus(StrEnum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"


class _Entity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Season(_Entity):
    id: Slug
    name: str = Field(min_length=1, max_length=100)
    number: PositiveInt
    roster_size: PositiveInt = 3
    draft_open: bool = True


class Contestant(_Entity):
    id: Slug
    season_id: Slug
    name: str = Field(min_length=1, max_length=100)
    tribe: str | None = None
    status: ContestantStatus = ContestantStatus.ACTIVE
    eliminated_episode: PositiveInt | None = None


class EpisodeStat(_Entity):
    """Event counts for one contestant in one episode. One record per pair."""

    season_id: Slug
    episode: PositiveInt
    contestant_id: Slug
    events: dict[EventType, NonNegativeInt] = Field(default_factory=dict)


class Roster(_Entity):
    """A player's picks for a season. One roster per user per season."""

    season_id: Slug
    user_id: str = Field(min_length=1, max_length=200)  # Auth0 ``sub``
    display_name: str = Field(min_length=1, max_length=50)
    contestant_ids: tuple[Slug, ...]

    @field_validator("contestant_ids")
    @classmethod
    def _unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("contestant_ids must be unique")
        return value
