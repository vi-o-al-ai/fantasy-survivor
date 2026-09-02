import pytest

from app.services.errors import RuleViolationError
from app.services.league import LeagueService
from app.storage.memory import MemoryStore
from tests.factories import contestant, season


def test_service_guards_duplicate_ids_for_direct_callers() -> None:
    store = MemoryStore()
    store.put_season(season("s49", roster_size=2))
    store.put_contestant(contestant("amy"))
    service = LeagueService(store)

    with pytest.raises(RuleViolationError, match="twice"):
        service.set_roster("s49", "u1", "P", ["amy", "amy"])
