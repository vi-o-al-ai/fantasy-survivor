"""Turn episode events into points, and rosters into a leaderboard.

Pure functions over in-memory data. The store supplies the inputs.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from app.domain.models import EpisodeStat, EventType, LeagueMember

DEFAULT_POINTS: Mapping[EventType, int] = MappingProxyType(
    {
        EventType.SURVIVED_EPISODE: 2,
        EventType.INDIVIDUAL_IMMUNITY: 10,
        EventType.TEAM_IMMUNITY: 3,
        EventType.INDIVIDUAL_REWARD: 5,
        EventType.TEAM_REWARD: 2,
        EventType.IDOL_FOUND: 8,
        EventType.IDOL_PLAYED_SUCCESSFULLY: 10,
        EventType.ADVANTAGE_FOUND: 5,
        EventType.CORRECT_VOTE: 3,
        EventType.VOTE_RECEIVED: -2,
        EventType.FIRE_MAKING_WIN: 8,
        EventType.VOTED_OUT: -5,
        EventType.QUIT_OR_MEDEVAC: -10,
        EventType.FINAL_THREE: 15,
        EventType.JURY_VOTE_RECEIVED: 3,
        EventType.SOLE_SURVIVOR: 30,
    }
)


@dataclass(frozen=True)
class ScoringRules:
    points: Mapping[EventType, int] = field(default_factory=lambda: DEFAULT_POINTS)

    @classmethod
    def with_overrides(cls, overrides: Mapping[EventType, int]) -> ScoringRules:
        """Defaults with a league's changes layered on top."""
        return cls(points=MappingProxyType({**DEFAULT_POINTS, **overrides}))

    def score(self, events: Mapping[EventType, int]) -> int:
        return sum(self.points.get(event, 0) * count for event, count in events.items())


DEFAULT_RULES = ScoringRules()


def contestant_totals(
    stats: Iterable[EpisodeStat], rules: ScoringRules = DEFAULT_RULES
) -> dict[str, int]:
    """Total points per contestant id across all given stats."""
    totals: dict[str, int] = defaultdict(int)
    for stat in stats:
        totals[stat.contestant_id] += rules.score(stat.events)
    return dict(totals)


@dataclass(frozen=True)
class LeaderboardEntry:
    user_id: str
    display_name: str
    points: int
    contestant_points: Mapping[str, int] = field(default_factory=dict)


def leaderboard(
    members: Iterable[LeagueMember], totals: Mapping[str, int]
) -> list[LeaderboardEntry]:
    """Rank members by roster points; ties broken by display name for stability."""
    entries = []
    for member in members:
        breakdown = {cid: totals.get(cid, 0) for cid in member.contestant_ids}
        entries.append(
            LeaderboardEntry(
                user_id=member.user_id,
                display_name=member.display_name,
                points=sum(breakdown.values()),
                contestant_points=breakdown,
            )
        )
    return sorted(entries, key=lambda e: (-e.points, e.display_name.lower(), e.user_id))
