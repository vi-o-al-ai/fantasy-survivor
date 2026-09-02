from typing import Annotated

from fastapi import APIRouter, Path, status

from app.auth import CurrentUserDep
from app.dependencies import LeagueDep
from app.domain.models import League, LeagueMember, Slug
from app.routers.common import ERROR_RESPONSES
from app.schemas import (
    JoinLeagueIn,
    LeaderboardEntryOut,
    LeagueCreateIn,
    LeagueOut,
    LeagueUpdateIn,
    RosterIn,
    ScoringRulesOut,
)

router = APIRouter(prefix="/leagues", tags=["leagues"], responses=ERROR_RESPONSES)

LeagueId = Annotated[Slug, Path()]


def _out(league: League, user_id: str) -> LeagueOut:
    is_owner = league.owner_id == user_id
    return LeagueOut(
        id=league.id,
        season_id=league.season_id,
        name=league.name,
        owner_id=league.owner_id,
        roster_size=league.roster_size,
        draft_open=league.draft_open,
        scoring_overrides=league.scoring_overrides,
        join_code=league.join_code if is_owner else None,
        is_owner=is_owner,
    )


@router.get("", response_model=list[LeagueOut])
def my_leagues(user: CurrentUserDep, league: LeagueDep) -> list[LeagueOut]:
    return [_out(lg, user.sub) for lg in league.leagues_for_user(user.sub)]


@router.post("", response_model=LeagueOut, status_code=status.HTTP_201_CREATED)
def create_league(body: LeagueCreateIn, user: CurrentUserDep, league: LeagueDep) -> LeagueOut:
    created = league.create_league(
        owner_id=user.sub,
        owner_display_name=body.display_name,
        season_id=body.season_id,
        name=body.name,
        roster_size=body.roster_size,
        scoring_overrides=body.scoring_overrides,
    )
    return _out(created, user.sub)


@router.get("/{league_id}", response_model=LeagueOut)
def get_league(league_id: LeagueId, user: CurrentUserDep, league: LeagueDep) -> LeagueOut:
    return _out(league.get_league_for_member(league_id, user.sub), user.sub)


@router.patch("/{league_id}", response_model=LeagueOut)
def update_league(
    league_id: LeagueId, body: LeagueUpdateIn, user: CurrentUserDep, league: LeagueDep
) -> LeagueOut:
    updated = league.update_league(league_id, user.sub, **body.model_dump(exclude_unset=True))
    return _out(updated, user.sub)


@router.get("/{league_id}/scoring-rules", response_model=ScoringRulesOut)
def league_scoring_rules(
    league_id: LeagueId, user: CurrentUserDep, league: LeagueDep
) -> ScoringRulesOut:
    lg = league.get_league_for_member(league_id, user.sub)
    return ScoringRulesOut(points=dict(league.rules_for(lg).points))


@router.post("/{league_id}/members", response_model=LeagueMember)
def join_league(
    league_id: LeagueId, body: JoinLeagueIn, user: CurrentUserDep, league: LeagueDep
) -> LeagueMember:
    return league.join_league(
        league_id, user_id=user.sub, display_name=body.display_name, join_code=body.join_code
    )


@router.get("/{league_id}/members", response_model=list[LeagueMember])
def list_members(
    league_id: LeagueId, user: CurrentUserDep, league: LeagueDep
) -> list[LeagueMember]:
    return league.list_members(league_id, user.sub)


@router.get("/{league_id}/members/me", response_model=LeagueMember)
def my_membership(league_id: LeagueId, user: CurrentUserDep, league: LeagueDep) -> LeagueMember:
    league.get_league(league_id)
    return league.get_member(league_id, user.sub)


@router.put("/{league_id}/members/me/roster", response_model=LeagueMember)
def set_my_roster(
    league_id: LeagueId, body: RosterIn, user: CurrentUserDep, league: LeagueDep
) -> LeagueMember:
    return league.set_roster(league_id, user.sub, body.contestant_ids)


@router.get("/{league_id}/leaderboard", response_model=list[LeaderboardEntryOut])
def get_leaderboard(
    league_id: LeagueId, user: CurrentUserDep, league: LeagueDep
) -> list[LeaderboardEntryOut]:
    return [
        LeaderboardEntryOut(
            rank=rank,
            user_id=entry.user_id,
            display_name=entry.display_name,
            points=entry.points,
            contestant_points=dict(entry.contestant_points),
        )
        for rank, entry in enumerate(league.leaderboard(league_id, user.sub), start=1)
    ]
