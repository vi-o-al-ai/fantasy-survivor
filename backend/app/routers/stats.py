from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.auth import CurrentUserDep, require_permission
from app.dependencies import LeagueDep
from app.domain.models import EpisodeStat, Slug
from app.schemas import EpisodeStatIn

router = APIRouter(prefix="/seasons/{season_id}", tags=["stats"])

WRITE_STATS = "write:stats"
WriteStats = Depends(require_permission(WRITE_STATS))
SeasonId = Annotated[Slug, Path()]
ContestantId = Annotated[Slug, Path()]
Episode = Annotated[int, Path(ge=1)]


@router.get("/stats", response_model=list[EpisodeStat])
def list_season_stats(
    season_id: SeasonId, _: CurrentUserDep, league: LeagueDep
) -> list[EpisodeStat]:
    return league.list_stats(season_id)


@router.get("/episodes/{episode}/stats", response_model=list[EpisodeStat])
def list_episode_stats(
    season_id: SeasonId, episode: Episode, _: CurrentUserDep, league: LeagueDep
) -> list[EpisodeStat]:
    return league.list_stats(season_id, episode)


@router.put(
    "/episodes/{episode}/stats/{contestant_id}",
    response_model=EpisodeStat,
    dependencies=[WriteStats],
)
def record_stat(
    season_id: SeasonId,
    episode: Episode,
    contestant_id: ContestantId,
    body: EpisodeStatIn,
    league: LeagueDep,
) -> EpisodeStat:
    return league.record_stat(season_id, episode, contestant_id, body.events)
