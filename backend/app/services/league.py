from __future__ import annotations

from collections.abc import Sequence

from app.domain.models import Contestant, EpisodeStat, EventType, Roster, Season
from app.domain.scoring import (
    DEFAULT_RULES,
    LeaderboardEntry,
    ScoringRules,
    contestant_totals,
    leaderboard,
)
from app.services.errors import NotFoundError, RuleViolationError
from app.storage.base import Store


class LeagueService:
    def __init__(self, store: Store, rules: ScoringRules = DEFAULT_RULES) -> None:
        self._store = store
        self._rules = rules

    # --- seasons ----------------------------------------------------------

    def list_seasons(self) -> list[Season]:
        return self._store.list_seasons()

    def get_season(self, season_id: str) -> Season:
        season = self._store.get_season(season_id)
        if season is None:
            raise NotFoundError("season", season_id)
        return season

    def upsert_season(self, season: Season) -> Season:
        self._store.put_season(season)
        return season

    # --- contestants ------------------------------------------------------

    def list_contestants(self, season_id: str) -> list[Contestant]:
        self.get_season(season_id)
        return self._store.list_contestants(season_id)

    def get_contestant(self, season_id: str, contestant_id: str) -> Contestant:
        contestant = self._store.get_contestant(season_id, contestant_id)
        if contestant is None:
            raise NotFoundError("contestant", contestant_id)
        return contestant

    def upsert_contestant(self, contestant: Contestant) -> Contestant:
        self.get_season(contestant.season_id)
        self._store.put_contestant(contestant)
        return contestant

    # --- episode stats ----------------------------------------------------

    def list_stats(self, season_id: str, episode: int | None = None) -> list[EpisodeStat]:
        self.get_season(season_id)
        return self._store.list_episode_stats(season_id, episode)

    def record_stat(
        self, season_id: str, episode: int, contestant_id: str, events: dict[EventType, int]
    ) -> EpisodeStat:
        self.get_season(season_id)
        self.get_contestant(season_id, contestant_id)
        stat = EpisodeStat(
            season_id=season_id, episode=episode, contestant_id=contestant_id, events=events
        )
        self._store.put_episode_stat(stat)
        return stat

    # --- rosters ----------------------------------------------------------

    def get_roster(self, season_id: str, user_id: str) -> Roster:
        self.get_season(season_id)
        roster = self._store.get_roster(season_id, user_id)
        if roster is None:
            raise NotFoundError("roster", user_id)
        return roster

    def set_roster(
        self, season_id: str, user_id: str, display_name: str, contestant_ids: Sequence[str]
    ) -> Roster:
        season = self.get_season(season_id)
        if not season.draft_open:
            raise RuleViolationError("the draft for this season is closed")
        if len(contestant_ids) != season.roster_size:
            raise RuleViolationError(f"a roster must have exactly {season.roster_size} contestants")
        if len(set(contestant_ids)) != len(contestant_ids):
            raise RuleViolationError("a roster cannot list the same contestant twice")
        known = {c.id for c in self._store.list_contestants(season_id)}
        unknown = sorted(set(contestant_ids) - known)
        if unknown:
            raise RuleViolationError(f"unknown contestants: {', '.join(unknown)}")
        roster = Roster(
            season_id=season_id,
            user_id=user_id,
            display_name=display_name,
            contestant_ids=tuple(contestant_ids),
        )
        self._store.put_roster(roster)
        return roster

    # --- scoring ----------------------------------------------------------

    def contestant_points(self, season_id: str) -> dict[str, int]:
        self.get_season(season_id)
        return contestant_totals(self._store.list_episode_stats(season_id), self._rules)

    def leaderboard(self, season_id: str) -> list[LeaderboardEntry]:
        totals = self.contestant_points(season_id)
        return leaderboard(self._store.list_rosters(season_id), totals)
