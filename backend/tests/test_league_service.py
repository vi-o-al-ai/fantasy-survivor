import pytest

from app.services.errors import RuleViolationError
from app.services.ids import new_join_code, new_league_id, slugify
from app.services.league import LeagueService
from app.storage.memory import MemoryStore
from tests.factories import contestant, league, member, season


def test_service_guards_duplicate_ids_for_direct_callers() -> None:
    store = MemoryStore()
    store.put_season(season("s49"))
    store.put_contestant(contestant("amy"))
    store.put_league(league("lg-1", roster_size=2))
    store.put_member(member("auth0|u1"))
    service = LeagueService(store)

    with pytest.raises(RuleViolationError, match="twice"):
        service.set_roster("lg-1", "auth0|u1", ["amy", "amy"])


def test_slugify_and_ids() -> None:
    assert slugify("  Jeff's  Big League!! ") == "jeff-s-big-league"
    assert slugify("!!!") == "league"
    assert slugify("a" * 50) == "a" * 24
    league_id = new_league_id("Jeff's League")
    assert league_id.startswith("jeff-s-league-") and len(league_id) == len("jeff-s-league-") + 6
    code = new_join_code()
    assert (len(code) == 8 and code.isupper()) or code.isdigit()
    assert new_join_code() != new_join_code()
