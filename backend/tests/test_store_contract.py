"""One behavioural contract, run against every Store implementation.

DynamoDB runs under moto (in-process mock), so no AWS or network involved.
"""

from collections.abc import Iterator

import pytest
from moto import mock_aws

from app.storage.base import Store
from app.storage.dynamodb import DynamoDBStore
from app.storage.memory import MemoryStore
from scripts.create_table import create_table
from tests.factories import contestant, roster, season, stat


@pytest.fixture
def memory_store() -> MemoryStore:
    return MemoryStore()


@pytest.fixture
def dynamodb_store(monkeypatch: pytest.MonkeyPatch) -> Iterator[DynamoDBStore]:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        assert create_table("test-table", region="us-east-1", endpoint_url=None)
        assert not create_table("test-table", region="us-east-1", endpoint_url=None)
        yield DynamoDBStore("test-table", region="us-east-1")


@pytest.fixture(params=["memory_store", "dynamodb_store"])
def store(request: pytest.FixtureRequest) -> Store:
    result: Store = request.getfixturevalue(request.param)
    return result


def test_seasons(store: Store) -> None:
    assert store.list_seasons() == []
    assert store.get_season("s49") is None

    store.put_season(season("s49"))
    store.put_season(season("s48", number=48))
    store.put_season(season("s49", name="Renamed"))  # put is upsert

    assert [s.id for s in store.list_seasons()] == ["s48", "s49"]
    got = store.get_season("s49")
    assert got is not None and got.name == "Renamed"


def test_contestants_are_scoped_to_season(store: Store) -> None:
    store.put_contestant(contestant("bob", "s49", tribe="Vati"))
    store.put_contestant(contestant("amy", "s49"))
    store.put_contestant(contestant("bob", "s48"))

    assert [c.id for c in store.list_contestants("s49")] == ["amy", "bob"]
    assert store.list_contestants("s47") == []
    got = store.get_contestant("s49", "bob")
    assert got is not None and got.tribe == "Vati"
    assert store.get_contestant("s49", "zed") is None


def test_episode_stats_filter_and_order(store: Store) -> None:
    store.put_episode_stat(stat("bob", 10, survived_episode=1))
    store.put_episode_stat(stat("amy", 2, survived_episode=1))
    store.put_episode_stat(stat("bob", 2, voted_out=1))
    store.put_episode_stat(stat("amy", 1, individual_immunity=1, season_id="s48"))

    all_stats = store.list_episode_stats("s49")
    assert [(s.episode, s.contestant_id) for s in all_stats] == [
        (2, "amy"),
        (2, "bob"),
        (10, "bob"),
    ]
    ep2 = store.list_episode_stats("s49", episode=2)
    assert [(s.episode, s.contestant_id) for s in ep2] == [(2, "amy"), (2, "bob")]
    assert store.list_episode_stats("s49", episode=1) == []


def test_episode_stat_upsert_replaces_events(store: Store) -> None:
    store.put_episode_stat(stat("bob", 1, survived_episode=1))
    store.put_episode_stat(stat("bob", 1, voted_out=1))

    stats = store.list_episode_stats("s49", episode=1)
    assert len(stats) == 1
    assert stats[0] == stat("bob", 1, voted_out=1)


def test_rosters(store: Store) -> None:
    assert store.get_roster("s49", "auth0|u1") is None

    store.put_roster(roster("auth0|u2", "bob"))
    store.put_roster(roster("auth0|u1", "amy", "bob"))
    store.put_roster(roster("auth0|u1", "amy", season_id="s48"))

    assert [r.user_id for r in store.list_rosters("s49")] == ["auth0|u1", "auth0|u2"]
    got = store.get_roster("s49", "auth0|u1")
    assert got is not None and got.contestant_ids == ("amy", "bob")


def test_dynamodb_key_layout(dynamodb_store: DynamoDBStore) -> None:
    """Pin the key scheme: it is the storage contract, changing it is a migration."""
    dynamodb_store.put_episode_stat(stat("bob", 7, survived_episode=1))
    dynamodb_store.put_roster(roster("auth0|u1", "bob"))
    dynamodb_store.put_season(season("s49"))

    items = dynamodb_store._table.scan()["Items"]
    keys = sorted((str(i["PK"]), str(i["SK"])) for i in items)
    assert keys == [
        ("SEASON#s49", "ROSTER#auth0|u1"),
        ("SEASON#s49", "STAT#EP007#bob"),
        ("SEASONS", "SEASON#s49"),
    ]
