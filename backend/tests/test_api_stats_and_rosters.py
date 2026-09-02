from fastapi.testclient import TestClient

from app.storage.memory import MemoryStore
from tests.conftest import bearer
from tests.factories import contestant, season


def seed(store: MemoryStore, **season_overrides: object) -> None:
    store.put_season(season("s49", **season_overrides))
    for cid in ("amy", "bob", "cal", "dee"):
        store.put_contestant(contestant(cid))


# --- stats ------------------------------------------------------------------


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


# --- rosters ----------------------------------------------------------------


def test_roster_lifecycle(
    client: TestClient, store: MemoryStore, auth_headers: dict[str, str]
) -> None:
    seed(store)

    assert client.get("/seasons/s49/rosters/me", headers=auth_headers).status_code == 404

    body = {"display_name": "Player One", "contestant_ids": ["amy", "bob", "cal"]}
    put = client.put("/seasons/s49/rosters/me", json=body, headers=auth_headers)
    assert put.status_code == 200
    assert put.json() == {
        "season_id": "s49",
        "user_id": "auth0|player1",
        "display_name": "Player One",
        "contestant_ids": ["amy", "bob", "cal"],
    }

    got = client.get("/seasons/s49/rosters/me", headers=auth_headers)
    assert got.json()["contestant_ids"] == ["amy", "bob", "cal"]


def test_roster_rules(client: TestClient, store: MemoryStore, auth_headers: dict[str, str]) -> None:
    seed(store)
    url = "/seasons/s49/rosters/me"

    too_few = client.put(
        url, json={"display_name": "P", "contestant_ids": ["amy"]}, headers=auth_headers
    )
    assert too_few.status_code == 409
    assert "exactly 3" in too_few.json()["detail"]

    unknown = client.put(
        url,
        json={"display_name": "P", "contestant_ids": ["amy", "bob", "zed"]},
        headers=auth_headers,
    )
    assert unknown.status_code == 409
    assert unknown.json() == {"detail": "unknown contestants: zed"}

    duplicate = client.put(
        url,
        json={"display_name": "P", "contestant_ids": ["amy", "amy", "bob"]},
        headers=auth_headers,
    )
    assert duplicate.status_code == 422


def test_roster_locked_when_draft_closed(
    client: TestClient, store: MemoryStore, auth_headers: dict[str, str]
) -> None:
    seed(store, draft_open=False)

    response = client.put(
        "/seasons/s49/rosters/me",
        json={"display_name": "P", "contestant_ids": ["amy", "bob", "cal"]},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "the draft for this season is closed"}


# --- leaderboard ------------------------------------------------------------


def test_leaderboard_end_to_end(
    client: TestClient, store: MemoryStore, admin_headers: dict[str, str]
) -> None:
    seed(store)
    p1 = bearer(sub="auth0|p1")
    p2 = bearer(sub="auth0|p2")
    client.put(
        "/seasons/s49/rosters/me",
        json={"display_name": "Alpha", "contestant_ids": ["amy", "bob", "cal"]},
        headers=p1,
    )
    client.put(
        "/seasons/s49/rosters/me",
        json={"display_name": "Bravo", "contestant_ids": ["bob", "cal", "dee"]},
        headers=p2,
    )
    client.put(
        "/seasons/s49/episodes/1/stats/amy",
        json={"events": {"survived_episode": 1, "individual_immunity": 1}},
        headers=admin_headers,
    )
    client.put(
        "/seasons/s49/episodes/1/stats/dee",
        json={"events": {"voted_out": 1}},
        headers=admin_headers,
    )

    board = client.get("/seasons/s49/leaderboard", headers=p1)

    assert board.status_code == 200
    assert board.json() == [
        {
            "rank": 1,
            "user_id": "auth0|p1",
            "display_name": "Alpha",
            "points": 12,
            "contestant_points": {"amy": 12, "bob": 0, "cal": 0},
        },
        {
            "rank": 2,
            "user_id": "auth0|p2",
            "display_name": "Bravo",
            "points": -5,
            "contestant_points": {"bob": 0, "cal": 0, "dee": -5},
        },
    ]
    points = client.get("/seasons/s49/points", headers=p1)
    assert points.json() == {"points": {"amy": 12, "dee": -5}}
