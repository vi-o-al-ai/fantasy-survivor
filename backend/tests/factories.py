"""Small builders so tests read as intent, not field lists."""

from __future__ import annotations

from app.domain.models import Contestant, EpisodeStat, EventType, League, LeagueMember, Season


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


def league(id: str = "lg-1", owner_id: str = "auth0|owner", **overrides: object) -> League:
    return League.model_validate(
        {
            "id": id,
            "season_id": "s49",
            "name": "Test League",
            "owner_id": owner_id,
            "join_code": "JOIN1234",
            **overrides,
        }
    )


def member(
    user_id: str, *contestant_ids: str, league_id: str = "lg-1", **overrides: object
) -> LeagueMember:
    return LeagueMember.model_validate(
        {
            "league_id": league_id,
            "user_id": user_id,
            "display_name": user_id.split("|")[-1],
            "contestant_ids": contestant_ids,
            **overrides,
        }
    )
