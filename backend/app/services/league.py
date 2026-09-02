from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.models import (
    Contestant,
    EpisodeStat,
    EventType,
    League,
    LeagueMember,
    Season,
)
from app.domain.scoring import (
    DEFAULT_RULES,
    LeaderboardEntry,
    ScoringRules,
    contestant_totals,
    leaderboard,
)
from app.services import ids
from app.services.errors import ForbiddenError, NotFoundError, RuleViolationError
from app.storage.base import Store


class LeagueService:
    """Use cases over the truth (seasons, stats) and user leagues."""

    def __init__(self, store: Store) -> None:
        self._store = store

    # --- seasons (truth) --------------------------------------------------

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

    def canonical_points(self, season_id: str) -> dict[str, int]:
        """Points per contestant under the default rules (the shared view)."""
        self.get_season(season_id)
        return contestant_totals(self._store.list_episode_stats(season_id), DEFAULT_RULES)

    # --- leagues ----------------------------------------------------------

    def create_league(
        self,
        *,
        owner_id: str,
        owner_display_name: str,
        season_id: str,
        name: str,
        roster_size: int,
        scoring_overrides: Mapping[EventType, int],
    ) -> League:
        self.get_season(season_id)
        league = League(
            id=ids.new_league_id(name),
            season_id=season_id,
            name=name,
            owner_id=owner_id,
            join_code=ids.new_join_code(),
            roster_size=roster_size,
            scoring_overrides=dict(scoring_overrides),
        )
        self._store.put_league(league)
        self._store.put_member(
            LeagueMember(league_id=league.id, user_id=owner_id, display_name=owner_display_name)
        )
        return league

    def get_league(self, league_id: str) -> League:
        league = self._store.get_league(league_id)
        if league is None:
            raise NotFoundError("league", league_id)
        return league

    def get_league_for_member(self, league_id: str, user_id: str) -> League:
        """Leagues are private: only members can see them."""
        league = self.get_league(league_id)
        if self._store.get_member(league_id, user_id) is None:
            raise ForbiddenError("you are not a member of this league")
        return league

    def leagues_for_user(self, user_id: str) -> list[League]:
        leagues = (
            self._store.get_league(lid) for lid in self._store.list_league_ids_for_user(user_id)
        )
        return sorted((lg for lg in leagues if lg is not None), key=lambda lg: lg.name.lower())

    def update_league(
        self,
        league_id: str,
        user_id: str,
        *,
        name: str | None = None,
        roster_size: int | None = None,
        draft_open: bool | None = None,
        scoring_overrides: Mapping[EventType, int] | None = None,
    ) -> League:
        league = self.get_league(league_id)
        if league.owner_id != user_id:
            raise ForbiddenError("only the league owner can change settings")
        changes: dict[str, object] = {}
        if name is not None:
            changes["name"] = name
        if roster_size is not None:
            changes["roster_size"] = roster_size
        if draft_open is not None:
            changes["draft_open"] = draft_open
        if scoring_overrides is not None:
            changes["scoring_overrides"] = dict(scoring_overrides)
        updated = league.model_copy(update=changes)
        self._store.put_league(updated)
        return updated

    def rules_for(self, league: League) -> ScoringRules:
        return ScoringRules.with_overrides(league.scoring_overrides)

    # --- members ----------------------------------------------------------

    def join_league(
        self, league_id: str, *, user_id: str, display_name: str, join_code: str
    ) -> LeagueMember:
        league = self.get_league(league_id)
        if league.join_code != join_code:
            raise ForbiddenError("wrong join code")
        existing = self._store.get_member(league_id, user_id)
        if existing is not None:
            return existing
        member = LeagueMember(league_id=league_id, user_id=user_id, display_name=display_name)
        self._store.put_member(member)
        return member

    def list_members(self, league_id: str, user_id: str) -> list[LeagueMember]:
        self.get_league_for_member(league_id, user_id)
        return self._store.list_members(league_id)

    def get_member(self, league_id: str, user_id: str) -> LeagueMember:
        member = self._store.get_member(league_id, user_id)
        if member is None:
            raise ForbiddenError("you are not a member of this league")
        return member

    def set_roster(
        self, league_id: str, user_id: str, contestant_ids: Sequence[str]
    ) -> LeagueMember:
        league = self.get_league(league_id)
        member = self.get_member(league_id, user_id)
        if not league.draft_open:
            raise RuleViolationError("the draft for this league is closed")
        if len(contestant_ids) != league.roster_size:
            raise RuleViolationError(f"a roster must have exactly {league.roster_size} contestants")
        if len(set(contestant_ids)) != len(contestant_ids):
            raise RuleViolationError("a roster cannot list the same contestant twice")
        known = {c.id for c in self._store.list_contestants(league.season_id)}
        unknown = sorted(set(contestant_ids) - known)
        if unknown:
            raise RuleViolationError(f"unknown contestants: {', '.join(unknown)}")
        updated = member.model_copy(update={"contestant_ids": tuple(contestant_ids)})
        self._store.put_member(updated)
        return updated

    # --- scoring ----------------------------------------------------------

    def league_points(self, league_id: str, user_id: str) -> dict[str, int]:
        league = self.get_league_for_member(league_id, user_id)
        stats = self._store.list_episode_stats(league.season_id)
        return contestant_totals(stats, self.rules_for(league))

    def leaderboard(self, league_id: str, user_id: str) -> list[LeaderboardEntry]:
        totals = self.league_points(league_id, user_id)
        return leaderboard(self._store.list_members(league_id), totals)
