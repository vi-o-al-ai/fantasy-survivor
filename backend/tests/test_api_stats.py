from fastapi.testclient import TestClient

from app.storage.memory import MemoryStore
from tests.factories import contestant, season


def seed(store: MemoryStore) -> None:
    store.put_season(season("s49"))
    for cid in ("amy", "bob", "cal", "dee"):
        store.put_contestant(contestant(cid))


def test_record_and_list_stats(
    client: TestClient, store: MemoryStore, admin_headers: dict[str, str]
) -> None:
    seed(store)

    put = client.put(
        "/seasons/s49/episodes/1/stats/amy",
        json={"events": {"survived_episode": 1, "individual_immunity": 1}},
        headers=admin_headers,
    )
    assert put.status_code == 200
    assert put.json() == {
        "season_id": "s49",
        "episode": 1,
        "contestant_id": "amy",
        "events": {"survived_episode": 1, "individual_immunity": 1},
    }

    by_episode = client.get("/seasons/s49/episodes/1/stats", headers=admin_headers)
    assert [s["contestant_id"] for s in by_episode.json()] == ["amy"]
    whole_season = client.get("/seasons/s49/stats", headers=admin_headers)
    assert len(whole_season.json()) == 1
    assert client.get("/seasons/s49/episodes/2/stats", headers=admin_headers).json() == []
    points = client.get("/seasons/s49/points", headers=admin_headers)
    assert points.json() == {"points": {"amy": 12}}


def test_stat_validation(
    client: TestClient, store: MemoryStore, admin_headers: dict[str, str]
) -> None:
    seed(store)
    url = "/seasons/s49/episodes/1/stats"

    unknown_contestant = client.put(f"{url}/zed", json={"events": {}}, headers=admin_headers)
    assert unknown_contestant.status_code == 404

    bad_event = client.put(f"{url}/amy", json={"events": {"won_lottery": 1}}, headers=admin_headers)
    assert bad_event.status_code == 422

    negative = client.put(f"{url}/amy", json={"events": {"voted_out": -1}}, headers=admin_headers)
    assert negative.status_code == 422

    episode_zero = client.put(
        "/seasons/s49/episodes/0/stats/amy", json={"events": {}}, headers=admin_headers
    )
    assert episode_zero.status_code == 422


def test_player_cannot_write_stats(
    client: TestClient, store: MemoryStore, auth_headers: dict[str, str]
) -> None:
    seed(store)
    response = client.put(
        "/seasons/s49/episodes/1/stats/amy", json={"events": {}}, headers=auth_headers
    )
    assert response.status_code == 403
