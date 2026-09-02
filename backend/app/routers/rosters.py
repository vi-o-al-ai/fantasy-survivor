from typing import Annotated

from fastapi import APIRouter, Path

from app.auth import CurrentUserDep
from app.dependencies import LeagueDep
from app.domain.models import Roster, Slug
from app.schemas import LeaderboardEntryOut, RosterIn

router = APIRouter(prefix="/seasons/{season_id}", tags=["rosters"])

SeasonId = Annotated[Slug, Path()]


@router.get("/rosters/me", response_model=Roster)
def get_my_roster(season_id: SeasonId, user: CurrentUserDep, league: LeagueDep) -> Roster:
    return league.get_roster(season_id, user.sub)


@router.put("/rosters/me", response_model=Roster)
def set_my_roster(
    season_id: SeasonId, body: RosterIn, user: CurrentUserDep, league: LeagueDep
) -> Roster:
    return league.set_roster(season_id, user.sub, body.display_name, body.contestant_ids)


@router.get("/leaderboard", response_model=list[LeaderboardEntryOut])
def get_leaderboard(
    season_id: SeasonId, _: CurrentUserDep, league: LeagueDep
) -> list[LeaderboardEntryOut]:
    return [
        LeaderboardEntryOut(
            rank=rank,
            user_id=entry.user_id,
            display_name=entry.display_name,
            points=entry.points,
            contestant_points=dict(entry.contestant_points),
        )
        for rank, entry in enumerate(league.leaderboard(season_id), start=1)
    ]
