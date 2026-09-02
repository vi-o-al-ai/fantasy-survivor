import pytest
from pydantic import ValidationError

from app.domain.models import EpisodeStat, EventType, LeagueMember, Season
from tests.factories import member, stat


def test_slug_ids_are_validated() -> None:
    with pytest.raises(ValidationError):
        Season(id="Not A Slug", name="x", number=1)


def test_roster_contestants_must_be_unique() -> None:
    with pytest.raises(ValidationError, match="unique"):
        member("auth0|u1", "a", "a")


def test_entities_are_frozen() -> None:
    s = Season(id="s1", name="One", number=1)
    with pytest.raises(ValidationError):
        s.name = "changed"  # type: ignore[misc]


def test_stat_events_use_enum_keys_and_nonnegative_counts() -> None:
    s = stat("a", individual_immunity=1)
    assert s.events == {EventType.INDIVIDUAL_IMMUNITY: 1}
    with pytest.raises(ValidationError):
        EpisodeStat(season_id="s1", episode=1, contestant_id="a", events={"nope": 1})
    with pytest.raises(ValidationError):
        EpisodeStat(season_id="s1", episode=1, contestant_id="a", events={EventType.VOTED_OUT: -1})


def test_json_round_trip() -> None:
    m = member("auth0|u1", "a", "b")
    assert LeagueMember.model_validate(m.model_dump(mode="json")) == m
