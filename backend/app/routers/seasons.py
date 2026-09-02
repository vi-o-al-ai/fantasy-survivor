from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.auth import CurrentUserDep, require_permission
from app.dependencies import LeagueDep
from app.domain.models import Contestant, Season, Slug
from app.domain.scoring import DEFAULT_RULES
from app.routers.common import ERROR_RESPONSES
from app.schemas import ContestantIn, ContestantPointsOut, ScoringRulesOut, SeasonIn

router = APIRouter(prefix="/seasons", tags=["seasons"], responses=ERROR_RESPONSES)

MANAGE_SEASONS = "manage:seasons"
ManageSeasons = Depends(require_permission(MANAGE_SEASONS))
SeasonId = Annotated[Slug, Path()]
ContestantId = Annotated[Slug, Path()]


@router.get("", response_model=list[Season])
def list_seasons(_: CurrentUserDep, league: LeagueDep) -> list[Season]:
    return league.list_seasons()


@router.get("/{season_id}", response_model=Season)
def get_season(season_id: SeasonId, _: CurrentUserDep, league: LeagueDep) -> Season:
    return league.get_season(season_id)


@router.put(
    "/{season_id}",
    response_model=Season,
    status_code=status.HTTP_200_OK,
    dependencies=[ManageSeasons],
)
def upsert_season(season_id: SeasonId, body: SeasonIn, league: LeagueDep) -> Season:
    return league.upsert_season(Season(id=season_id, **body.model_dump()))


@router.get("/{season_id}/contestants", response_model=list[Contestant])
def list_contestants(season_id: SeasonId, _: CurrentUserDep, league: LeagueDep) -> list[Contestant]:
    return league.list_contestants(season_id)


@router.put(
    "/{season_id}/contestants/{contestant_id}",
    response_model=Contestant,
    dependencies=[ManageSeasons],
)
def upsert_contestant(
    season_id: SeasonId, contestant_id: ContestantId, body: ContestantIn, league: LeagueDep
) -> Contestant:
    contestant = Contestant(id=contestant_id, season_id=season_id, **body.model_dump())
    return league.upsert_contestant(contestant)


@router.get("/{season_id}/points", response_model=ContestantPointsOut)
def contestant_points(
    season_id: SeasonId, _: CurrentUserDep, league: LeagueDep
) -> ContestantPointsOut:
    """Points per contestant under the default rules (the shared, canonical view)."""
    return ContestantPointsOut(points=league.canonical_points(season_id))


scoring_router = APIRouter(tags=["scoring"], responses=ERROR_RESPONSES)


@scoring_router.get("/scoring-rules", response_model=ScoringRulesOut)
def scoring_rules(_: CurrentUserDep) -> ScoringRulesOut:
    return ScoringRulesOut(points=dict(DEFAULT_RULES.points))
