"""Small builders so tests read as intent, not field lists."""

from __future__ import annotations

from app.domain.models import Contestant, EpisodeStat, EventType, Roster, Season


def season(id: str = "s49", **overrides: object) -> Season:
    return Season.model_validate({"id": id, "name": f"Season {id}", "number": 49, **overrides})


def contestant(id: str, season_id: str = "s49", **overrides: object) -> Contestant:
    return Contestant.model_validate(
        {"id": id, "season_id": season_id, "name": id.title(), **overrides}
    )


def stat(
    contestant_id: str,
    episode: int = 1,
    season_id: str = "s49",
    **events: int,
) -> EpisodeStat:
    return EpisodeStat(
        season_id=season_id,
        episode=episode,
        contestant_id=contestant_id,
        events={EventType(k): v for k, v in events.items()},
    )


def roster(
    user_id: str, *contestant_ids: str, season_id: str = "s49", **overrides: object
) -> Roster:
    return Roster.model_validate(
        {
            "season_id": season_id,
            "user_id": user_id,
            "display_name": user_id.split("|")[-1],
            "contestant_ids": contestant_ids,
            **overrides,
        }
    )
