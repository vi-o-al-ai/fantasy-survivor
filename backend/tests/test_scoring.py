from app.domain.models import EventType
from app.domain.scoring import (
    DEFAULT_POINTS,
    DEFAULT_RULES,
    ScoringRules,
    contestant_totals,
    leaderboard,
)
from tests.factories import member, stat


def test_every_event_type_has_default_points() -> None:
    assert set(DEFAULT_POINTS) == set(EventType)


def test_score_multiplies_counts() -> None:
    events = {EventType.VOTE_RECEIVED: 3, EventType.SURVIVED_EPISODE: 1}

    assert DEFAULT_RULES.score(events) == 3 * -2 + 2


def test_score_ignores_unknown_events_in_custom_rules() -> None:
    rules = ScoringRules(points={EventType.SOLE_SURVIVOR: 100})

    assert rules.score({EventType.SOLE_SURVIVOR: 1, EventType.VOTED_OUT: 1}) == 100


def test_contestant_totals_sum_across_episodes() -> None:
    stats = [
        stat("a", 1, survived_episode=1),
        stat("a", 2, survived_episode=1, individual_immunity=1),
        stat("b", 1, voted_out=1),
    ]

    assert contestant_totals(stats) == {"a": 2 + 2 + 10, "b": -5}


def test_leaderboard_ranks_and_breaks_ties_by_name() -> None:
    totals = {"a": 10, "b": 5, "c": 5}
    members = [
        member("auth0|zed", "b", "c", display_name="Zed"),
        member("auth0|amy", "a", "missing", display_name="Amy"),
        member("auth0|bob", "b", "c", display_name="bob"),
    ]

    board = leaderboard(members, totals)

    assert [(e.display_name, e.points) for e in board] == [("Amy", 10), ("bob", 10), ("Zed", 10)]
    assert board[0].contestant_points == {"a": 10, "missing": 0}


def test_leaderboard_empty() -> None:
    assert leaderboard([], {}) == []


def test_member_without_roster_scores_zero() -> None:
    board = leaderboard([member("auth0|new")], {"a": 10})
    assert board[0].points == 0
    assert board[0].contestant_points == {}


def test_overrides_layer_on_defaults() -> None:
    rules = ScoringRules.with_overrides({EventType.SOLE_SURVIVOR: 100, EventType.VOTED_OUT: 0})

    assert rules.points[EventType.SOLE_SURVIVOR] == 100
    assert rules.points[EventType.VOTED_OUT] == 0
    assert (
        rules.points[EventType.INDIVIDUAL_IMMUNITY] == DEFAULT_POINTS[EventType.INDIVIDUAL_IMMUNITY]
    )
