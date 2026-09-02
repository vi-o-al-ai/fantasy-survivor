"""In-memory store for tests and throwaway local runs. Not thread-safe."""

from __future__ import annotations

from app.domain.models import Contestant, EpisodeStat, Roster, Season


class MemoryStore:
    def __init__(self) -> None:
        self._seasons: dict[str, Season] = {}
        self._contestants: dict[tuple[str, str], Contestant] = {}
        self._stats: dict[tuple[str, int, str], EpisodeStat] = {}
        self._rosters: dict[tuple[str, str], Roster] = {}

    def list_seasons(self) -> list[Season]:
        return sorted(self._seasons.values(), key=lambda s: s.id)

    def get_season(self, season_id: str) -> Season | None:
        return self._seasons.get(season_id)

    def put_season(self, season: Season) -> None:
        self._seasons[season.id] = season

    def list_contestants(self, season_id: str) -> list[Contestant]:
        return sorted(
            (c for (sid, _), c in self._contestants.items() if sid == season_id),
            key=lambda c: c.id,
        )

    def get_contestant(self, season_id: str, contestant_id: str) -> Contestant | None:
        return self._contestants.get((season_id, contestant_id))

    def put_contestant(self, contestant: Contestant) -> None:
        self._contestants[(contestant.season_id, contestant.id)] = contestant

    def list_episode_stats(self, season_id: str, episode: int | None = None) -> list[EpisodeStat]:
        return sorted(
            (
                s
                for (sid, ep, _), s in self._stats.items()
                if sid == season_id and (episode is None or ep == episode)
            ),
            key=lambda s: (s.episode, s.contestant_id),
        )

    def put_episode_stat(self, stat: EpisodeStat) -> None:
        self._stats[(stat.season_id, stat.episode, stat.contestant_id)] = stat

    def list_rosters(self, season_id: str) -> list[Roster]:
        return sorted(
            (r for (sid, _), r in self._rosters.items() if sid == season_id),
            key=lambda r: r.user_id,
        )

    def get_roster(self, season_id: str, user_id: str) -> Roster | None:
        return self._rosters.get((season_id, user_id))

    def put_roster(self, roster: Roster) -> None:
        self._rosters[(roster.season_id, roster.user_id)] = roster
